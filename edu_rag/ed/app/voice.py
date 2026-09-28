import speech_recognition as sr
import pyttsx3
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
import time

# Function to initialize text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say what you want to search on YouTube.")
        print("Listening for your search command...")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        speak("There was a network error.")
        return None

# Set the path to msedgedriver
driver_path = "msedgedriver.exe"  # Replace with the actual path to msedgedriver if needed
service = Service(driver_path)

# Initialize Edge WebDriver
driver = webdriver.Edge(service=service)

# Open YouTube
# driver.get('https://www.youtube.com')
# time.sleep(3)  # Wait for the page to load

# Get voice input for search
search_query = listen()

if search_query:
    # Locate the search bar and enter the query
    search_bar = driver.find_element("name", "search_query")
    search_bar.send_keys(search_query)
    search_bar.send_keys(Keys.RETURN)  # Press Enter to execute search
    speak(f"Searching for {search_query} on YouTube.")
else:
    speak("No search query was provided, closing YouTube.")

# Allow time to load results
time.sleep(5)
driver.quit()
