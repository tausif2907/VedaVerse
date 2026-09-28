# utils.py

def process_mcq_questions(response):
    """
    Process the response from the RAG application to match each question with options and the correct answer.
    """
    questions = []
    
    for item in response:
        question_text = item.get('question', '').strip()
        options = item.get('options', [])
        correct_answer = item.get('correct_answer', '').strip().upper()

        question_data = {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        }
        
        questions.append(question_data)
    
    return questions


def generate_mcq_questions(qa):
    """
    Generates a list of MCQs using the RAG application and formats them for scoring.
    """
    rag_response = qa.run("Generate multiple-choice questions with options and indicate the correct answer.")
    formatted_questions = process_mcq_questions(rag_response)
    return formatted_questions
from openai import OpenAI
from django.conf import settings


def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_topic_from_user_input(user_input):
    try:
        response = get_openai_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extract the main topic from this input: {user_input}"}
            ],
            max_tokens=60
        )

        # Extract the topic from the response
        topic = response.choices[0].message.content.strip()
        return topic
    except Exception as e:
        print(f"Error processing input with OpenAI: {e}")
        return None
from googleapiclient.discovery import build
from django.conf import settings

def get_youtube_videos_by_topic(topic):
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    
    # Perform a search query on YouTube based on the topic
    request = youtube.search().list(
        q=topic,  # Search term is the extracted topic
        part="snippet",
        type="video",  # Only videos have an id.videoId
        maxResults=5,  # Limit results to 5 videos
    )
    
    response = request.execute()
    videos = []
    
    for item in response.get("items", []):
        video = {
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
        }
        videos.append(video)
    
    return videos