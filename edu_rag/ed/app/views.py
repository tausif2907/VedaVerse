import os
import chromadb.api
import chromadb.api.shared_system_client
from django.shortcuts import render, redirect,HttpResponse
from .models import PDFDocument
from .forms import PDFUploadForm
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_openai import OpenAI
from gtts import gTTS
from django.conf import settings
import os
from gtts import gTTS
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import PDFDocument  
from PyPDF2 import PdfReader  
from django.core.files.storage import FileSystemStorage
from .new3 import takecommand
import random
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import openai
# Ensure your OpenAI API key is set via environment variable OPENAI_API_KEY
from .utils import get_topic_from_user_input, get_youtube_videos_by_topic
#takecommand()
def home(request):
    #takecommand()
    return render(request,'intro.html')
def upload_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()
    return render(request, 'upload_pdf.html', {'form': form})

def pdf_list(request):
    pdfs = PDFDocument.objects.all()
    audio_folder = os.path.join(settings.MEDIA_ROOT, 'audio')
    audio_files = []

    
    if os.path.exists(audio_folder):
        audio_files = [
            f"audio/{file}" for file in os.listdir(audio_folder) if file.endswith('.mp3')
        ]
    return render(request, 'pdf_list.html', {'pdfs': pdfs,'audio_files': audio_files})

from django.core.files.storage import FileSystemStorage

def convert_pdf_to_speech(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)
    
    
    pdf_path = pdf.pdf_file.path  
    title = pdf.title
    
    
    audio_file_name = convert_pdf_to_speech_function(pdf_path, title)

    
    return redirect('ask_question', pdf_id=pdf_id)

def convert_pdf_to_speech_function(pdf_path, title):
    """
    Convert the entire PDF text to speech and return the audio file path.
    """
   
    loader = PdfReader(pdf_path)
    full_text = ""
    for page in loader.pages:
        full_text += page.extract_text()

    tts = gTTS(text=full_text, lang='en')
    
    audio_file_name = f"{title.replace(' ', '_')}.mp3"
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
    
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'audio')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'audio'))

    tts.save(audio_file_path)

    return audio_file_name
from langdetect import detect
import chromadb
def ask_question(request, pdf_id):
    pdf = PDFDocument.objects.get(id=pdf_id)
    pdf_path = pdf.pdf_file.path
    audio_file = pdf.audio_file.name if pdf.audio_file else None  

    if request.method == "POST":
        
        query = request.POST.get('query')
    
        topic = get_topic_from_user_input(query)
        
        if topic:
            videos = get_youtube_videos_by_topic(topic)

        try:
            language = detect(query)  
        except Exception as e:
            return render(request, 'ask_question.html', {
                'pdf': pdf,
                'error': f"Error detecting language: {str(e)}"
            })

        
        rag_app = create_rag_app(pdf_path)

        try:
            result = rag_app.run(f"{query}\nPlease respond in the same language as the input.").replace("\n", " ")

            if not result:
                result = "Sorry, no relevant information was found in the document."
        except Exception as e:
            return render(request, 'ask_question.html', {
                'pdf': pdf,
                'error': f"Error retrieving answer: {str(e)}"
            })

        if 'convert_to_speech' in request.POST:
            try:
                audio_file_name = convert_pdf_to_speech(pdf_path, pdf.title)  
                pdf.audio_file = f'audio/{audio_file_name}'  
                pdf.save()  
                audio_file = pdf.audio_file.name  
            except Exception as e:
                return render(request, 'ask_question.html', {
                    'pdf': pdf,
                    'result': result,
                    'query': query,
                    'error': f"Error converting PDF to speech: {str(e)}"
                })

        return render(request, 'ask_question.html', {
            'topic': topic,
            'videos': videos,
            'pdf': pdf,
            'result':result,  
            'query': query,
            'audio_file': audio_file 
        })

    return render(request, 'ask_question.html', {'pdf': pdf, 'audio_file': audio_file})

import os
from pathlib import Path

def create_rag_app(pdf_path):
    """
    Creates a RAG application using LangChain, OpenAI, and ChromaDB, 
    storing vector embeddings persistently for each PDF and clearing ChromaDB cache after every request.
    """
   
    embeddings_dir = Path("persistent_embeddings")
    embeddings_dir.mkdir(exist_ok=True)

    
    pdf_id = Path(pdf_path).stem
    db_path = embeddings_dir / f"{pdf_id}_chroma"

    
    if db_path.exists():
        print(f"Loading existing embeddings for PDF: {pdf_id}")
        db = Chroma(persist_directory=str(db_path), embedding_function=OpenAIEmbeddings())
    else:
        print(f"Creating new embeddings for PDF: {pdf_id}")
       
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings, persist_directory=str(db_path))
        db.persist() 

    
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)

    return qa


from django.shortcuts import render, get_object_or_404, redirect
from .models import PDFDocument
from gtts import gTTS
import os
from django.conf import settings

from django.shortcuts import render, get_object_or_404
from .models import PDFDocument  

def text_to_speech_view(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)

    audio_file = pdf.audio_file.name if pdf.audio_file else None  

    if request.method == "POST":
        # Call your conversion function here
        audio_file_name = convert_pdf_to_speech_function(pdf.pdf_file.path, pdf.title) 
        pdf.audio_file = f'audio/{audio_file_name}' 
        pdf.save()  
        audio_file = pdf.audio_file.name  

   
    all_pdfs = PDFDocument.objects.all()

    return render(request, 'text_to_speech.html', {
        'pdf': pdf,
        'audio_file': audio_file,
        'pdfs': all_pdfs  
    })


def convert_pdf_to_speech_function(pdf_path, title):
    """
    Convert the entire PDF text to speech and return the audio file path.
    """
   
    loader = PdfReader(pdf_path)
    full_text = ""
    for page in loader.pages:
        full_text += page.extract_text()

    tts = gTTS(text=full_text, lang='en')
    
    audio_file_name = f"{title.replace(' ', '_')}.mp3"
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
    
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'audio')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'audio'))

    tts.save(audio_file_path)

    return audio_file_name
import os
from django.conf import settings
from django.shortcuts import render, HttpResponse
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))

def prep_image(image_path):
    """Uploads the image file and returns the sample file object."""
    sample_file = genai.upload_file(path=image_path, display_name="Diagram")
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    return sample_file

def extract_text_from_image(sample_file, prompt):
    """Generates content based on the uploaded image and the given prompt."""
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content([sample_file, prompt])
    return response.text

def upload_screenshot_view(request):
    if request.method == 'POST':
        sample_file=prep_image('sketch_screenshot.png')
        text = extract_text_from_image(sample_file, "Analyze handwritten equations or problems in mathematics, physics, or chemistry. Accurately extract the content and solve them step by step, providing concise and clear explanations for each step. Focus on correctness and clarity, avoiding unnecessary details. For context-specific equations, provide appropriate units and references. Below are examples for guidance:---**Mathematics Example:**Equation: 2 𝑥 + 3 = 11 2x+3=11Solution:1.Subtract3frombothsides: 2 𝑥 = 8 2x=82.Divideby2: 𝑥 = 4 x=4Example2:Solve \intx 2 𝑑 𝑥 \intx 2 dx.Solution:1.Applythepowerrule: 𝑥 𝑛 + 1 𝑛 + 1 + 𝐶 n+1 x n+1 ​ +C.2.Result: 𝑥 3 3 + 𝐶 3 x 3 ​ +C.---**Physics Example:**Problem:Acaracceleratesuniformlyfromresttoavelocityof 20 m/s 20m/sin 5 seconds 5seconds.Findtheacceleration.Solution:1.Usetheformula 𝑣 = 𝑢 + 𝑎 𝑡 v=u+at.2.Rearrangetofind 𝑎 = 𝑣 − 𝑢 𝑡 a= t v−u ​ .3.Substituting: 𝑎 = 20 − 0 5 = 4 m/s 2 a= 5 20−0 ​ =4m/s 2 .Example2:Calculatethekineticenergyofa 2 kg 2kgobjectmovingat 3 m/s 3m/s.Solution:1.Use 𝐾 𝐸 = 1 2 𝑚 𝑣 2 KE= 2 1 ​ mv 2 .2.Substituting: 𝐾 𝐸 = 1 2 × 2 × 3 2 = 9 J KE= 2 1 ​ ×2×3 2 =9J.---**Chemistry Example:**Problem:Calculatethenumberofmolesin 44 g 44gof 𝐶 𝑂 2 CO 2 ​ (Molarmass = 44 g/mol =44g/mol).Solution:1.Use 𝑛 = 𝑚 𝑀 n= M m ​ .2.Substituting: 𝑛 = 44 44 = 1 mol n= 44 44 ​ =1mol.Example2:Balancetheequation: 𝐻 2 + 𝑂 2 \rightarrowH 2 𝑂 H 2 ​ +O 2 ​ \rightarrowH 2 ​ O.Solution:1.Balance 𝐻 2 H 2 ​ : 2 𝐻 2 + 𝑂 2 → 2 𝐻 2 𝑂 2H 2 ​ +O 2 ​ →2H 2 ​ O.---Byprovidingthisstructuredpromptwithexamples,theAIwillbetterunderstandhowtoextractandsolvehandwrittenequationsinthesesubjects,focusingonclarity,accuracy,andsteps.")
        text_list=text.split(",")
        return render(request, "sketch_opened.html", {'text_list': text_list}) 



from django.shortcuts import render, redirect
from django.http import HttpResponse
import subprocess
import os
def open_sketchbook(request):
    sketchbook_path = os.path.join(os.path.dirname(__file__), 'sketch.py')
    subprocess.Popen(["python", sketchbook_path])    
    return redirect('sketch_opened')  


def sketch_opened(request):
    """A confirmation page to show that the Sketchbook has been opened."""
    return render(request, 'sketch_opened.html')

# views.py
from django.shortcuts import render
from django.http import JsonResponse
import os
from .frames import capture_frame
from .pdf import create_pdf_from_images

folder_path = os.path.join(os.path.dirname(__file__), 'Folder_with_Frames')

def capture_frame_view(request):
    """View to capture a frame when the user clicks a button."""
    if request.method == 'POST':
       
        frame_index = request.POST.get('frame_index', 0)
        capture_frame(frame_index)
        return JsonResponse({'status': 'Frame captured!', 'frame_index': frame_index})
    
    return JsonResponse({'status': 'Invalid request'}, status=400)

def create_pdf_view(request):
    """View to create a PDF from captured frames."""
    if request.method == 'POST':
        create_pdf_from_images(folder_path)
        return JsonResponse({'status': 'PDF created!'})
    
    return JsonResponse({'status': 'Invalid request'}, status=400)
def photos(request):
    return render(request,'photos.html')


def generate_mcq_questions(qa, num_questions=10):
    question_prompt = "Using GPT-4.0. Dont add comma(,) in options. Generate ten multiple-choice quiz questions based on the document, with four answer options each and an indication of the correct answer. Format as: Q: <question> Options: A) ..., B) ..., C) ..., D) ... Correct: <option>."
    
    response = qa.run(question_prompt)
    
    questions = []
    for line in response.split("\n"):
        if "Q:" in line:
            question_text = line.split("Q:")[1].strip()
            questions.append({"question": question_text, "options": [], "correct_answer": None})
        elif "Options:" in line and questions:
            options = line.split("Options:")[1].split(", ")
            questions[-1]["options"] = [option.strip() for option in options]
        elif "Correct:" in line and questions:
            correct_option = line.split("Correct:")[1].strip().split(")")[0]  
            if correct_option:  
                questions[-1]["correct_answer"] = correct_option

    
    questions = [q for q in questions if q["correct_answer"] and q["options"]]
    
    print(questions)
    return questions[:num_questions]


def quiz_view(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)
    pdf_path = pdf.pdf_file.path
    qa = create_rag_app(pdf_path)

    

    if request.method == "POST":

        user_answers = [request.POST.get(f"answer_{i}", "") for i in range(len(request.session['mcq']))]  
        score = 0
        feedback = []

        print("\n")
        print("\n")
        print("\n")


        print(request.session['mcq'],user_answers)
        print(request.session['mcq']["0"])

        print("\n")
        print("\n")
        print("\n")

        for i in range(len(request.session['mcq'])):
            correct_answer = request.session['mcq'][str(i)][1]
            user_answer = user_answers[i].strip().upper() if user_answers[i] else ""  

            
            print(f"Question {i+1}:")
            print(f"Correct Answer: {correct_answer}")
            print(f"User Answer: {user_answer}")
            print("\n")

            print("these are the answers: ",len(user_answer),user_answer," || ",correct_answer)
            if user_answer and (user_answer[0] == correct_answer):
                score += 1
                feedback.append("Correct")
            else:
                feedback.append(f"Incorrect (Correct answer: {correct_answer})")
            print("\n")


        zipped_data = [[request.session['mcq'][str(i)][0],user_answers[i],feedback[i]] for i in range(len(request.session['mcq']))]
        return render(request, 'quiz_results.html', {
            'zipped_data': zipped_data,
            'score': score,
            'total': len(request.session['mcq']),
            'pdf_id': pdf_id  
        })

    mcqs = generate_mcq_questions(qa)
    request.session['mcq']={i:[mcqs[i]['question'],mcqs[i]['correct_answer']] for i in range(len(mcqs))}

    return render(request, 'quiz.html', {'mcqs': mcqs})
videos = []
def generate_flowchart(request, name):
    project_name = name
    openai.api_key = os.environ.get('OPENAI_API_KEY', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in generating project workflows. Maintain the input language throughout the conversation."
                },
                {
                    "role": "user",
                    "content": f"Give Steps to make '{project_name}' in 5-10 lines."
                },
            ]
        )
        topic = get_topic_from_user_input(name)
       
        
        if topic:
            videos = get_youtube_videos_by_topic(topic)
        
        flowchart_data = response['choices'][0]['message']['content']
        print(f"OpenAI Response: {flowchart_data}")  # Debugging
        print(f"Videos ",videos)
        if videos:
            return JsonResponse({
            "flowchart": flowchart_data,
            "videos": videos
            }, status=200)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        return JsonResponse({"error": str(e)}, status=500)


def flowchart(request):
    return render(request,"flowchart.html",{"videos":videos})
import speech_recognition as sr

def process_voice(request):
    """Process voice input and return transcribed text."""
    if request.method == 'POST':
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
                
                text = recognizer.recognize_google(audio)
                return JsonResponse({'text': text})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'})

def process_voice_kn(request):
    """Process Kannada voice input."""
    if request.method == 'POST':
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as inputs:
                print("Please speak now")
                listening = recognizer.listen(inputs, timeout=5)  # Listen for 5 seconds
                print("Analysing...")
                
                try:
                    transcribed_text = recognizer.recognize_google(listening, language="kn-IN")
                    print("Did you say: " + transcribed_text)  # Debug log
                    return JsonResponse({'text': transcribed_text})  # Send response with Kannada text
                except:
                    print("Please speak again")
                    return JsonResponse({'error': 'Could not understand your speech. Please try again.'})
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug log
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'})

def process_voice_HI(request):
    """Process voice input and return transcribed text in Hindi."""
    if request.method == 'POST':
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
                
                text = recognizer.recognize_google(audio, language="hi-IN")  # 'hi-IN' for Hindi
                return JsonResponse({'text': text})  # Output will be in Hindi script
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'})

from googleapiclient.discovery import build
from django.conf import settings

from django.shortcuts import render
from .utils import get_topic_from_user_input, get_youtube_videos_by_topic

def recommend_videos(request):
    if request.method == 'POST':
        user_input = request.POST.get('query')
        topic = get_topic_from_user_input(user_input)
        
        if topic:
            videos = get_youtube_videos_by_topic(topic)
            return render(request, 'videos_list.html', {'videos': videos, 'topic': topic})
    
    return render(request, 'search.html')