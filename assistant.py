import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
import sys
from time import sleep 
import webbrowser
import pyttsx3 as tts
import speech_recognition as sr
import random
from datetime import datetime
import nepali_datetime 
import pyautogui
from pyjokes import get_joke
import requests
import geocoder
import platform
import ctypes
import os
import subprocess

# Load intents
with open("intents.json", "r") as file:
    data = json.load(file)

# Prepare training data
patterns = []
labels = []
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(pattern.lower())
        labels.append(intent["tag"])

# Preprocessing and model pipeline
vectorizer = TfidfVectorizer()
classifier = LinearSVC()
model = make_pipeline(vectorizer, classifier)

# Train the model
model.fit(patterns, labels)

# Function to predict intent
def predict_intent(text):
    return model.predict([text.lower()])[0]

# Function to get a response or execute a function
def get_response(intent, user_input=""):
    for item in data["intents"]:
        if item["tag"] == intent:
            if "function" in item:
                return globals()[item["function"]](user_input) if "arguments" in item else globals()[item["function"]]()
            return random.choice(item["responses"])
    return "Sorry, I didn’t catch that."

# Initialize text-to-speech engine
engine = tts.init("sapi5")
speaker = sr.Recognizer()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 180)

def date_and_time():
    date = datetime.now().strftime("%d %B %Y %A")
    time = datetime.now().strftime("%I:%M %p")
    return f"Time is {time} and date is {date}."

def nepali_date():
    return nepali_datetime.datetime.now().strftime("%d %B %Y %A")

def open_app(user_input):
    user_input = user_input.replace("open", "").strip()
    
    if "." in user_input:
        website_name = "https://" + user_input
        webbrowser.open(website_name)
    else:
        pyautogui.press("super")
        sleep(1)
        pyautogui.typewrite(user_input)
        sleep(2)
        pyautogui.press('enter')
    
    return f"Opening {user_input}"

def lock_pc():
    speak("Locking the PC")
    ctypes.windll.user32.LockWorkStation()
    return "Locking the PC..."

def poweroff():
    os.system("shutdown /s /t 10")
    return "Shutting down PC in 10 seconds."

def reboot():
    os.system("shutdown /r /t 10")
    return "Restarting PC in 10 seconds."

def sleep_pc():
    if platform.system() == 'Windows':
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif platform.system() == 'Linux':
        subprocess.run(["systemctl", "suspend"])
    elif platform.system() == 'Darwin':
        subprocess.run(["pmset", "sleepnow"])
    return "Putting PC to sleep."

def jokes():
    return get_joke()

def location():
    try:
        loc = geocoder.ip("me")
        if loc.city and loc.country:
            return f"Your current location is {loc.city}, {loc.country}."
        return "Unable to determine location."
    except Exception as e:
        return f"Error fetching location: {e}"

def weather():
    try:
        with open("apikey", "r") as f:
            API_KEY = f.read().strip()
        
        loc = geocoder.ip("me")
        if not loc.city:
            return "Unable to determine location for weather."
        
        url = f"http://api.openweathermap.org/data/2.5/weather?appid={API_KEY}&q={loc.city}&units=metric"
        response = requests.get(url).json()
        
        temp_celsius = response['main']['temp']
        temp_feels_like = response['main']['feels_like']
        weather_type = response['weather'][0]["description"]
        
        return f"The temperature is {temp_celsius:.2f}°C, but it feels like {temp_feels_like:.2f}°C. The weather is {weather_type}."
    except Exception as e:
        return f"Could not fetch weather data. Error: {e}"

def speak(text: str):
    engine.say(text)
    engine.runAndWait()

def exit_assistant():
    speak("Goodbye!")
    sys.exit(0)

# Wake word detection
WAKE_WORD = "xavier"

def listen_for_wake_word():
    with sr.Microphone() as source:
        print("Waiting for wake word 'Xavier'...")
        speaker.adjust_for_ambient_noise(source, duration=0.5) # type: ignore
        while True:
            try:
                audio = speaker.listen(source, timeout=None, phrase_time_limit=3)
                text = speaker.recognize_google(audio, language="en").lower() # type: ignore
                print(f"Heard: {text}")
                if WAKE_WORD in text:
                    speak("Yes, I’m here! How can I assist you?")
                    return True
            except sr.UnknownValueError:
                continue  # Keep listening if nothing clear is heard
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                speak("There’s an issue with my ears. Please try again.")
                continue

def listen_for_command():
    with sr.Microphone() as source:
        print("Listening for your command...")
        speaker.adjust_for_ambient_noise(source, duration=0.5) # type: ignore
        try:
            audio = speaker.listen(source, timeout=8)
            print("Understanding...")
            text = speaker.recognize_google(audio, language="en").lower() # type: ignore
            print("You:", text)
            return text
        except sr.UnknownValueError:
            speak("I didn’t catch that. Could you repeat?")
            return ""
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            speak("There’s an issue with the speech service.")
            return ""
        except sr.WaitTimeoutError:
            speak("I didn’t hear anything. Still here for you!")
            return ""

def assistant():
    speak("Hello, I am Xavier. Say my name to wake me up!")
    print("\n\n << Note: Say 'Xavier' to activate, then give a command. E.g., 'Xavier open Chrome' >> \n\n")
    
    while True:
        # Step 1: Listen for wake word
        if listen_for_wake_word():
            # Step 2: Listen for the actual command after wake word
            user_input = listen_for_command()
            if user_input:
                intent = predict_intent(user_input)
                response = get_response(intent, user_input)
                speak(response)
                print("Assistant:", response)
                
                if intent == "goodbye":
                    exit_assistant()

if __name__ == "__main__":
    assistant()