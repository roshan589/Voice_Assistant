import speech_recognition as sr
import time

def set_alarm(user_input):

    if user_input.lower() == "set alarm" or user_input.lower() == "set an alarm":
        speak("Alright, for when?")
        print("Alright, for when?")

        def listen_alarm():
            recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=8)

                try:
                    print("Understanding...")
                    alarm_time = recognizer.recognize_google(audio, language="en")
                    alarm_time = alarm_time.replace("at", "").replace("for", "").replace(".", "").strip().upper()
                    print("You: ", alarm_time)

                    alarm_list = alarm_time.split(":")
                    hour, mins = map(int, alarm_list[:2])

                    if "PM" in alarm_time and hour < 12:
                        hour += 12

                    if hour >= 24 or mins >= 60:
                        print("Invalid time. Please try again.")
                        return

                    current_time = time.localtime()
                    alarm_timestamp = time.mktime((current_time.tm_year, current_time.tm_mon, current_time.tm_mday,
                                                   hour, mins, 0, 0, 0, -1))

                    time_difference = alarm_timestamp - time.mktime(current_time)
                    if time_difference <= 0:
                        print("Invalid time. Please set the alarm for a future time.")
                        return

                    time.sleep(time_difference)
                    print("Alarm is ringing!")
                    # Add your alarm ringing logic here.

                except sr.UnknownValueError:
                    print("Sorry, I could not understand the time. Please try again.")
                except sr.RequestError as e:
                    print(f"Error with the speech recognition service: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")

        listen_alarm()

# Replace the following line with your actual speak function
def speak(message):
    print(message)

# Replace the following line with your actual alarm.ring_alarm function
class Alarm:
    @staticmethod
    def ring_alarm(hour, mins, period):
        print(f"Alarm set for {hour}:{mins} {period}")

# Example usage:
set_alarm("set an alarm")
