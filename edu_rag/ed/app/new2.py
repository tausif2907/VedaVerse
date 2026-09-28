import webbrowser
import wikipedia
import pyttsx3
import speech_recognition as sr
import datetime
import os
import pywhatkit as kit
import sys
from requests import get
import pyjokes
import smtplib
import speech_recognition as sr
import pyttsx3
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
driver_path = "app\msedgedriver.exe"  # Replace with the actual path to msedgedriver if needed
service = Service(driver_path)

# Initialize Edge WebDriver
driver = webdriver.Edge(service=service)
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


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[0].id)
def jarvis(query):
    if "hello jarvis" in query:
        speak("Hello sir")
    elif "open PDF" in query:
        driver.get('http://127.0.0.1:8000/pdfs/')
    
    elif "open chat history" in query:
        driver.get('http://127.0.0.1:8000/ask/1/')
        
    elif "open Hitler biography" in query:
        driver.get('http://127.0.0.1:8000/ask/2/')
        speak("Please say what you want to search on Chat")
        listen()
        #enter_text(search_query)
    elif "open ecology" in query:
        driver.get('http://127.0.0.1:8000/ask/3/')
    elif "open who ias" in query:
        driver.get('http://127.0.0.1:8000/ask/4/')
    elif "open upload" in query:
        driver.get('http://127.0.0.1:8000/upload/')
    elif "close" in query:
        driver.quit()
    

def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()
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
    except Exception as e:
        speak("Say that again please")
        return "none"
    return jarvis(query)
# def enter_text(text):
#     #driver.get(url)  # Open the target URL
    
#     input_box = driver.find_element("name", "query")  # Locate the input box by name attribute
#     input_box.clear()  # Clear any existing text
#     input_box.send_keys(text)  # Enter the specified text
#     submit_button = driver.find_element("css selector", "button[type='submit']")  # Locate the submit button
#     submit_button.click()  # Click the submit button
#     speak("Text entered and submitted successfully.")
    # except Exception as e:
    #     speak("An error occurred while entering text.")
    #     print(e)
def enter_text(text):
    try:
        input_box = driver.find_element("name", "query")  # Locate the input box by name attribute
        input_box.clear()  # Clear any existing text
        input_box.send_keys(text)  # Enter the specified text
        submit_button = driver.find_element("css selector", "button[type='submit']")  # Locate the submit button
        submit_button.click()  # Click the submit button
        speak("Text entered and submitted successfully.")
    except Exception as e:
        speak("An error occurred while entering text.")
        print(e) 