# VedaVerse

**An AI-powered, voice-first learning platform built to make education accessible for blind and visually impaired learners.**

VedaVerse turns ordinary study material (PDFs, handwritten problems, topics you speak aloud) into something you can *talk to* and *listen to*. It combines Retrieval-Augmented Generation (RAG) over your documents with speech recognition, text-to-speech, and multimodal AI, all served through a Django web app.

---

## ✨ Features

| Feature | What it does | Route |
|---|---|---|
| 📄 **Chat with your PDFs (RAG)** | Upload a PDF and ask questions about it. Answers come from the document's content and in the same language you asked in. | `/upload/`, `/pdfs/`, `/ask/<pdf_id>/` |
| 🔊 **PDF → Audiobook** | Converts an entire PDF into an MP3 with Google Text-to-Speech so it can be listened to. | `/text_to_speech/<pdf_id>/` |
| 📝 **Auto-generated Quizzes** | Generates multiple-choice questions from a PDF, then scores your answers and gives feedback. | `/quiz/<pdf_id>/` |
| 🎙️ **Multilingual Voice Input** | Speech-to-text in **English**, **Kannada** and **Hindi**. | `/process-voice/`, `/process-voice_kn/`, `/process-voice_HI/` |
| ✍️ **Sketchbook Problem Solver** | Opens a drawing canvas. Write a math, physics or chemistry problem by hand, and Gemini reads it and solves it step by step. | `/open_sketchbook/`, `/upload_screenshot/` |
| 🧭 **Workflow AI** | Describe a project and get a 5–10 step workflow from GPT-4o, plus related YouTube tutorials. | `/flowchart/`, `/flowchart/generate/<name>/` |
| 🎥 **Video Recommendations** | Pulls the main topic out of your query and recommends relevant YouTube videos. | `/search/` |
| 📷 **Webcam → PDF** | Captures frames from the webcam and stitches them into a single PDF. | `/capture_frame/`, `/create_pdf/` |

---

## 🧠 How It Works

```
 🎙️ Voice / ⌨️ Text query
          │
          ▼
 Speech Recognition ──► Language detection (langdetect)
          │
          ▼
 ┌───────────────────── RAG pipeline (LangChain) ─────────────────────┐
 │  PDF ─► PyPDFLoader ─► CharacterTextSplitter (1000 chars)          │
 │      ─► OpenAI Embeddings ─► ChromaDB (persisted per PDF)          │
 │      ─► Retriever ─► RetrievalQA (OpenAI LLM) ─► Answer            │
 └────────────────────────────────────────────────────────────────────┘
          │
          ▼
 Answer shown on page  +  🔊 gTTS / pyttsx3 audio  +  🎥 related YouTube videos
```

Embeddings are stored in `persistent_embeddings/<pdf_name>_chroma/`, so each PDF is embedded only once. Later questions about the same PDF reuse the stored vectors.

---

## 🛠️ Tech Stack

- **Backend:** Django (SQLite)
- **RAG / LLM:** LangChain, OpenAI (embeddings, completions, GPT-4 / GPT-4o), ChromaDB
- **Vision:** Google Gemini 1.5 Pro (handwritten equation solving)
- **Speech:** SpeechRecognition (Google Web Speech API), gTTS, pyttsx3
- **Documents & media:** PyPDF2, Pillow, OpenCV
- **External APIs:** YouTube Data API v3
- **Desktop tools:** Tkinter (sketchbook), Selenium + Edge WebDriver (voice-driven browsing)

---

## 📁 Project Structure

```
VedaVerse/
├── edu_rag/ed/                  # Django project (run everything from here)
│   ├── manage.py
│   ├── ed/                      # Project settings & root URLs
│   │   ├── settings.py
│   │   └── urls.py
│   ├── app/                     # Main application
│   │   ├── views.py             # RAG, TTS, quiz, voice, flowchart, video views
│   │   ├── urls.py              # App routes
│   │   ├── models.py            # PDFDocument model
│   │   ├── utils.py             # Topic extraction (OpenAI) + YouTube search
│   │   ├── sketch.py            # Tkinter sketchbook, sends drawings to the server
│   │   ├── gemini.py            # Gemini image-to-solution helpers
│   │   ├── frames.py / pdf.py   # Webcam frame capture & images-to-PDF
│   │   ├── assistant.py, new3.py, voice.py   # Voice assistant experiments
│   │   ├── phraser.py, imagegenrations.py, pdfupdate.py  # Experimental: FLAN-T5 rephrasing,
│   │   │                                                 # Stable Diffusion, PDF rewriting
│   │   └── templates/           # HTML templates
│   ├── static/                  # Images, video & audio assets
│   ├── media/                   # Uploaded PDFs & generated audio (created at runtime)
│   └── persistent_embeddings/   # ChromaDB vector stores, one per PDF (created at runtime)
├── jarvis.py                    # Standalone desktop voice assistant
├── main.py                      # Selenium / Edge WebDriver demo
├── requirements.txt
├── .env.example                 # Template for your API keys & settings
└── readme.txt                   # Original project write-up
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- A working **microphone** (for voice features) and a **webcam** (for frame capture)
- API keys for **OpenAI**, **Google Gemini**, and **YouTube Data API v3**
- Windows is recommended: some modules use the `sapi5` TTS voice and Microsoft Edge WebDriver

### 1. Clone the repository

```bash
git clone https://github.com/tausif2907/VedaVerse.git
cd VedaVerse
```

### 2. Create a virtual environment

```bash
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> On Windows, if `PyAudio` fails to install, run `pip install pipwin && pipwin install pyaudio`, or install a prebuilt wheel.

### 4. Configure your keys

Copy the example file and fill in your own values:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

| Variable | Needed for |
|---|---|
| `OPENAI_API_KEY` | PDF Q&A, quizzes, Workflow AI, topic extraction |
| `GEMINI_API_KEY` | Sketchbook problem solver |
| `YOUTUBE_API_KEY` | Video recommendations |
| `DJANGO_SECRET_KEY` | Django (any long random string) |
| `DJANGO_DEBUG` / `DJANGO_ALLOWED_HOSTS` | Set `False` and add your hosts when deploying |
| `JARVIS_*` | Optional, only for the desktop voice assistant |

`.env` is git-ignored and loaded automatically by Django and `jarvis.py`. **Never commit it.**

### 5. Run migrations and start the server

```bash
cd edu_rag/ed
python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## 📖 Usage

1. **Upload a PDF** at `/upload/`. It then appears in the list at `/pdfs/`.
2. **Ask questions** about the PDF by typing or speaking. The answer comes with related YouTube videos.
3. **Listen** to the whole document by turning it into audio on the text-to-speech page.
4. **Test yourself** with a quiz generated from the PDF at `/quiz/<pdf_id>/`.
5. **Solve handwritten problems**: open the sketchbook, write the problem, and click **"Check this"**. Gemini returns a step-by-step solution.
6. **Plan a project** in Workflow AI at `/flowchart/`.

### Standalone scripts

```bash
python jarvis.py   # Desktop voice assistant (Wikipedia, YouTube, jokes, apps, email...)
python main.py     # Opens YouTube through Edge WebDriver
```

- `jarvis.py` reads its email, WhatsApp and file-path settings from the `JARVIS_*` variables in `.env`. For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your account password.
- The Selenium scripts need `msedgedriver.exe`. It isn't committed, so [download](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) the version that matches your Edge browser and place it next to the script (or in `edu_rag/ed/app/`).

---

## ⚠️ Known Limitations

- **Voice input runs on the server:** voice routes record from the microphone of the machine running Django, not the browser. This works only for local use.
- **Windows-first:** the voice assistants use the `sapi5` TTS engine and Edge WebDriver.
- **Experimental modules:** `phraser.py` and `imagegenrations.py` download large Hugging Face models (FLAN-T5, Stable Diffusion 2) and are not wired into the URLs.

---

## 🌍 Impact

- **Accessibility:** voice in, audio out, so learners don't need to see the screen.
- **Independence:** learners can explore, question and test themselves on any document without help from someone else.
- **Inclusivity:** multilingual input (English, Kannada, Hindi) reaches more learners.

---

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.
