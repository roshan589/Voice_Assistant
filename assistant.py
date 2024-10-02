import json

from time import sleep 
import webbrowser
from click import argument
from portalocker import AlreadyLocked
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


# Initialize the engine
engine = tts.init("sapi5")
speaker = sr.Recognizer()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 180)

# Load intents from JSON file
def load_intents(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data: dict = json.load(file)
    return data


def find_best_match(user_input: str, intents: list[dict]) -> str | None:
    user_input_lower = user_input.lower()
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern in user_input_lower:
                return intent["tag"]
    return None


def get_response(tag: str, intents: dict,user_input: str) -> str | None:
    for q in intents["intents"]:
        if q["tag"] == tag:
          if "function" in q and "arguments" in q:
            return globals()[q["function"]](user_input) 
          elif "function" in q:
            return globals()[q["function"]]()
          elif "responses" in q:
              return random.choice(q["responses"])

    return None


def date_and_time():
    date = datetime.now().strftime("%d %B %Y %A")
    time = datetime.now().strftime("%I:%M %p ") # type: ignore
    return f"Time is {time} and date is {str(date)}"


def nepali_date():
    date = nepali_datetime.datetime.now().strftime("%d %B %Y %A")
    return date 

def open_app(user_input):
    if "." in user_input:
        user_input  = user_input.replace("open ","")
        user_input = user_input.replace("Max","")
        website_name = "https://www."+user_input
        webbrowser.open(website_name)
        
    else:
        user_input  = user_input.replace("open","")
        user_input = user_input.replace("Max","")
        pyautogui.press("super")
        sleep(1)
        pyautogui.typewrite(user_input)
        sleep(2)
        pyautogui.press('enter')
    return "Opening "+ user_input
        

def lock_pc():
    speak("locking the pc")
    ctypes.windll.user32.LockWorkStation()
    return "Locking the pc...."
    

def poweroff():
    os.system("shutdown /s /t 10")
    return "shuttting down pc in 10 seconds"


def reboot():
    os.system("shutdown /r /t 10") 
    return "Restarting pc in 10 seconds"


def sleep_pc():
    # Put the computer to sleep based on the platform
    if platform.system() == 'Windows':
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif platform.system() == 'Linux':
        subprocess.run(["systemctl", "suspend"])
    elif platform.system() == 'Darwin':
        subprocess.run(["pmset", "sleepnow"])


def jokes():
    joke = get_joke()
    return joke


def location():
    location = geocoder.ip("me")
    city,country = location.city, location.country
    notice = "This location is extracted from the IP address. So, It may be inaccurate."
    print(notice)
    speak(notice)
    return "Your current location is "+city+","+country
    

def weather():
  BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
  API_KEY = open("apikey","r").read()
  location = geocoder.ip("me")
  CITY = location.city
  url = BASE_URL+ "appid="+ API_KEY + "&q="+ CITY
  response = requests.get(url).json()
  def temp_converter(temp_kelvin):
    celsius  = temp_kelvin - 273.15
    fahernheit = celsius*(9/5) + 32
    return celsius, fahernheit
  temp_kelvin = response['main']['temp']
  temp_celsius, temp_fahernheit = temp_converter(temp_kelvin)
  temp_feels_like_kelvin = response['main']['feels_like']
  temp_feels_like_celsius,temp_feels_like_fahernheit = temp_converter(temp_feels_like_kelvin)
  weather_type = response['weather'][0]["description"]
  return f"The temperature is {temp_celsius:.2f}°C, but it feels like {temp_feels_like_celsius:.2f}°C and the weather is {weather_type}"


def set_alarm(user_input):

    if user_input == "set alarm" or user_input =="set an alarm":
        speak("Alright, for when?")
        print("Alright, for when?")
        def listen_alarm():
            with sr.Microphone() as source:
                print("Listening...")
                audio = speaker.listen(source,0,8)
                speaker.adjust_for_ambient_noise(source,duration = 0.5) # type: ignore
                try:
                    print("Understanding...")
                    alarm_time = speaker.recognize_google(audio, language="en",) # type: ignore
                    alarm_time = alarm_time.replace("at","")
                    alarm_time = alarm_time.replace("at","")
                    alarm_time = alarm_time.replace("for","")
                    alarm_time = alarm_time.replace(".","")
                    alarm_time = alarm_time.upper()
                    print("You: ",alarm_time)
                    alarm_list = alarm_time.split(":")
                    alarm_list[1:] = alarm_list[1].split()
                    hour, mins, period = map(str, alarm_list)  # Move this line inside the try block
                    return hour, mins, period

                    
                    
                except sr.UnknownValueError:
                    return ""
                except sr.RequestError as e:
                    print(f"Error with the speech recognition service; {e}")
                    return ""
                except TimeoutError as e:
                    return ""
            
        hour, mins, period = listen_alarm()  # Call the function and get the values
        if hour and mins and period:
            alarm.ring_alarm(int(hour), int(mins), period)    
        
        
        
        


def speak(text: str):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = speaker.listen(source,0,8)
        speaker.adjust_for_ambient_noise(source,duration = 0.5) # type: ignore
        try:
            print("Understanding...")
            text = speaker.recognize_google(audio, language="en",) # type: ignore
            print("You: ", text)
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Error with the speech recognition service; {e}")
            return ""
        except TimeoutError as e:
            return ""

def assistant():
    intents: dict = load_intents("intents.json")

    speak("Hello, I am Max. How can I help you?")
    print("\n\n << Note: Say the domain if you want to open the website. For eg: 'youtube.com'>> \n\n")
    while True:
        user_input: str = str(listen()).lower()


        if user_input == "exit":
            speak("Goodbye!")
            break
        
            

        best_match: str | None = find_best_match(user_input, intents["intents"])

        if best_match:
            answer: str = get_response(best_match, intents,user_input) # type: ignore
            print(f"Assistant: {answer}")
            speak(answer)     

        

        else:
            print("Assistant: Sorry, I didn't understand.")
    



if __name__ == "__main__":
    assistant()
 