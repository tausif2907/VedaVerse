import webbrowser
import wikipedia
import pyttsx3
#import speech_recognition as sr
import datetime
import os
import pywhatkit as kit
import sys
from requests import get
import pyjokes
import smtplib
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys

# Initialize WebDriver
driver_path = r"app\msedgedriver.exe"  # Replace with the actual path if needed
driver = None

def get_driver():
    global driver
    if driver is None:
        service = Service(driver_path)
        driver = webdriver.Edge(service=service)
    return driver

# Initialize speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[0].id)

# Function to speak text
def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()

# Listen function for voice commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say what you want to search on Chat")
        print("Listening for your search command...")
        audio = recognizer.listen(source)
        
    try:
        query = recognizer.recognize_google(audio)
        if query:
            enter_text(query)
            return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
    except sr.RequestError:
        speak("There was a network error.")
    return None

# Main assistant function for handling commands
def jarvis(query):
    d = get_driver()
    if "hello jarvis" in query:
        speak("Hello sir")
    elif "open PDF" in query:
        d.get('http://127.0.0.1:8000/pdfs/')
    elif "open chat history" in query:
        d.get('http://127.0.0.1:8000/ask/1/')
    elif "open Hitler biography" in query:
        d.get('http://127.0.0.1:8000/ask/2/')
        speak("Please say what you want to search on Chat")
        listen()
    elif "open ecology" in query:
        d.get('http://127.0.0.1:8000/ask/3/')
    elif "open who ias" in query:
        d.get('http://127.0.0.1:8000/ask/4/')
    elif "open upload" in query:
        d.get('http://127.0.0.1:8000/upload/')
    elif "close" in query:
        d.quit()

# Command function to handle the user's primary input
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1
        audio = r.listen(source, timeout=7, phrase_time_limit=6)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}")
        if query != "none":
            jarvis(query)
    except Exception as e:
        speak("Say that again please")
        return "none"

# Function to enter text on a webpage
def enter_text(text):
    try:
        d = get_driver()
        input_box = d.find_element("name", "query")
        input_box.clear()
        input_box.send_keys(text)
        submit_button = d.find_element("css selector", "button[type='submit']")
        submit_button.click()
        speak("Text entered and submitted successfully.")
    except Exception as e:
        speak("An error occurred while entering text.")
        print(e)
