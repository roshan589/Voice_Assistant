from winotify import Notification, audio
from datetime import datetime
import time

def ring_alarm(alarm_hour, alarm_min, alarm_period):
    current_datetime = datetime.now()
    current_hour = int(current_datetime.strftime("%I"))
    current_min = int(current_datetime.strftime("%M"))
    current_period = current_datetime.strftime("%p")
    while True:
        if alarm_hour == current_hour and alarm_min == current_min and alarm_period == current_period:
            toast = Notification(app_id="Alarm", title="Alarm Clock Ringing")
            toast.set_audio(audio.LoopingAlarm, loop=True)
            toast.show()

            # Add a delay to avoid constant checking and reduce CPU usage
            time.sleep(1)

