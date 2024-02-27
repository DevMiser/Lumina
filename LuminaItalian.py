# the following program is provided by DevMiser - https://github.com/DevMiser

# to use this file, you must download the file porcupine_params_it.pv from
# https://github.com/Picovoice/porcupine/tree/master/lib/common and place it
# in the/home/pi/.local/lib/python3.9/site-packages/pvleopard/lib/common folder 
# on your Raspberry Pi
# You must also download the file leopard_params_it.pv from
# https://github.com/Picovoice/leopard/tree/master/lib/common and place it
# in the /home/pi/.local/lib/python3.9/site-packages/pvleopard/lib/common folder
# on your Raspberry Pi
# You must also create a new wake word in Italian using the Picovoice console
# (https://console.picovoice.ai/), choose Raspberry Pi as the Platform, download the file,
# and put it in the /home/pi/.local/lib/python3.9/site-packages/pvporcupine/resources/keyword_files/raspberry-pi 
# folder on your Raspberry Pi
# In the wake_word() function below, replace "Lumina" with your new wake word

#!/usr/bin/env python3

import datetime
import io
import openai
import os
import pyaudio
import pvcobra
import pvleopard
import pvporcupine
import schedule
import struct
import sys
import textwrap
import threading
import time
import tkinter as tk
import urllib.request

from openai import OpenAI
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageTk
from pvleopard import *
from pvrecorder import PvRecorder
from time import sleep
from threading import Thread

openai.api_key = "put your secret API key between these quotation marks"
pv_access_key= "put your secret access key between these quotation marks"

client = OpenAI(api_key=openai.api_key)

audio_stream = None
cobra = None
pa = None
porcupine = None
recorder = None
global text_var
global screen_width, screen_height

count = 0

CloseProgram_list = ["Close program",
    "End program",
    "Exit program",
    "Stop program",
    "Close the program",
    "End the program",
    "Exit the program",
    "Stop the program",
    "Exit"
    ]

DisplayOn_list = ["Turn on",
    "Wake up"
    ]

DisplayOff_list = ["Turn off",
    "Sleep"
    ]

Save_list = ["Save",
    "Keep",
    "Save it",
    "Keep it",
    "Save image",
    "Keep image",
    "Save the image",
    "Keep the image",
    "Save that image",
    "Keep that image"
    ]

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#screen_width = x
#screen_height = y
root['bg'] = 'black'
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.overrideredirect(True)
root.attributes("-fullscreen", True)
root.update()

def close_image_window():

    windows = root.winfo_children()
    for window in windows:
        if isinstance(window, tk.Toplevel):
            if window.attributes("-fullscreen"):
                print("closing image window")
                window.destroy()

def close_program():

    recorder = Recorder()
    recorder.stop()
    o.delete
    recorder = None
    sys.exit ("Program terminated")

def current_time():

    time_now = datetime.datetime.now()
    formatted_time = time_now.strftime("%m-%d-%Y %I:%M %p\n")
    print("The current date and time is:", formatted_time)
    
def dall_e3(prompt):  
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
#        quality="hd",
        n=1,
    )
    return (response.data[0].url)

def detect_silence():

    cobra = pvcobra.create(access_key=pv_access_key)

    silence_pa = pyaudio.PyAudio()

    cobra_audio_stream = silence_pa.open(
                    rate=cobra.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=cobra.frame_length)

    last_voice_time = time.time()

    while True:
        
        cobra_pcm = cobra_audio_stream.read(cobra.frame_length)
        cobra_pcm = struct.unpack_from("h" * cobra.frame_length, cobra_pcm)      
        if cobra.process(cobra_pcm) > 0.2:
            last_voice_time = time.time()
        else:
            silence_duration = time.time() - last_voice_time
            if silence_duration > 0.8:                
                print("End of query detected\n")
                cobra_audio_stream.stop_stream                
                cobra_audio_stream.close()
                cobra.delete()
                last_voice_time=None
                break

def display_on(transcript):
    
    for word in DisplayOn_list:
        if word in transcript:
            print("\'"f"{word}\' detected")
            current_time
            os.system("xset dpms force on")
            print("\nTurning on display.")
            sleep(1)
            
def display_off(transcript):   
 
    for word in DisplayOff_list:
        if word in transcript:
            print("\'"f"{word}\' detected")
            current_time
            print("\nTurning off display.")
            os.system("xset dpms force off")
            sleep(1)

def draw_request(transcript):

    global text_var

    prompt = transcript
    print("You requested the following image: " + prompt)
    print("\nCreating image...\n")
    
    wrapped_prompt = textwrap.fill(prompt, width=35) 
    
    text_var.set("Generating new image...\n\n" + wrapped_prompt)
    text_window.update()
  
    image_url = dall_e3(transcript)

    print("Displaying generated image.")    
          
    update_image(image_url) 

def listen():
    global image_window
    global text_window
    global text_var
    cobra = pvcobra.create(access_key=pv_access_key)
    
    close_image_window()

    listen_pa = pyaudio.PyAudio()

    listen_audio_stream = listen_pa.open(
                rate=cobra.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=cobra.frame_length)
    Statement = "Listening"
    text_var.set("Listening")
    text_window.update()
 
    print("Listening...")

    while True:
        listen_pcm = listen_audio_stream.read(cobra.frame_length)
        listen_pcm = struct.unpack_from("h" * cobra.frame_length, listen_pcm)
           
        if cobra.process(listen_pcm) > 0.3:
            print("Voice detected")
            listen_audio_stream.stop_stream
            listen_audio_stream.close()
            cobra.delete()
            break

def display_logo():
    global image_window
    global screen_width, screen_height
    image_window = tk.Toplevel(root)
    image_window.title("Image Window")
    image_window.geometry(f"{screen_width}x{screen_height}+0+0")
    image_window.attributes("-fullscreen", True)
    image_window.overrideredirect(True)
    image_window.configure (bg='black')
    image = Image.open("/home/pi/Lumina/Lumina Logo.png")
    # Calculate the scaling factor based on the original image size and the screen size
    original_width, original_height = image.size
    scale = max(screen_width / original_width, screen_height / original_height)
    # Resize the image with the scaled dimensions
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)
    image = image.resize((scaled_width, scaled_height)) 
    image_photo = ImageTk.PhotoImage(image)
    image_canvas = tk.Canvas(image_window, bg='#000000', width=screen_width, height=screen_height)
    # Center the image on the screen
    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2
    image_canvas.create_image(x, y, image=image_photo, anchor=tk.NW)
    image_canvas.pack()
    image_window.update()

def on_message (transcript, DisplayOn_list, DisplayOff_list, CloseProgram_list, Save_list):

    words = transcript.split(',')
    for word in words:
        if word in CloseProgram_list:
            close_program()
        elif word in DisplayOn_list:         
            display_on(transcript)
        elif word in DisplayOff_list:
            display_off(transcript)
        elif word in Save_list:
            save_image(image_label) 
        else:
            draw_request(transcript)

def save_image(image_label):       
    global text_var
    global text_window
    global image
    global image_window 
    global screen_width, screen_height
    timestamp = datetime.datetime.now().strftime("%m-%d-%Y")
    saved_images_path = "/home/pi/Lumina/"
    output_filename = f"{saved_images_path}{image_label}_{timestamp}.png"
    image.save(output_filename, format="PNG")
    save_message = (f"Image saved as\n\n" + output_filename)
    print(save_message)
    wrapped_save_message = textwrap.fill(save_message, width=60)
    text_var.set(wrapped_save_message)
    text_window.update()
    sleep(3)
    image_window = tk.Toplevel(root)
    image_window.title("Image Window")
    image_window.geometry(f"{screen_width}x{screen_height}+0+0")
    image_window.attributes("-fullscreen", True)
    image_window.overrideredirect(True)
    image_window.configure (bg='black') 
    image = image
    original_width, original_height = image.size
    scale = max(screen_width / original_width, screen_height / original_height)
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)
    image = image.resize((scaled_width, scaled_height)) 
    image_photo = ImageTk.PhotoImage(image)
    image_canvas = tk.Canvas(image_window, bg='#000000', width=screen_width, height=screen_height)
    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2
    image_canvas.create_image(x, y, image=image_photo, anchor=tk.NW)
    image_canvas.pack()
    image_window.update()

def text_window_func():
    global text_var
    global text_window
    global screen_width, screen_height
    text_window = tk.Toplevel(root)
    text_window.geometry(f"{screen_width}x{screen_height}+0+0")
    text_window.overrideredirect(True)
    text_window.focus_set()
    text_window.configure (bg='black')
    text_var = tk.StringVar()
    label = tk.Label(text_window, textvariable=text_var, bg='#000000',fg='#ADD8E6', font=("Arial Black", 72))
    label.pack(side=tk.TOP, anchor=tk.CENTER, pady=screen_height//4)
    print("text window open")
    text_window.update()

def update_image(image_url):
    global image
    global image_window 
    global screen_width, screen_height
    image_window = tk.Toplevel(root)
    image_window.title("Image Window")
    image_window.geometry(f"{screen_width}x{screen_height}+0+0")
    image_window.attributes("-fullscreen", True)
    image_window.overrideredirect(True)
    image_window.configure (bg='black') 
    raw_data = urllib.request.urlopen(image_url).read()
    image = Image.open(io.BytesIO(raw_data))
    original_width, original_height = image.size
    scale = max(screen_width / original_width, screen_height / original_height)
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)
    image = image.resize((scaled_width, scaled_height)) 
    image_photo = ImageTk.PhotoImage(image)
    image_canvas = tk.Canvas(image_window, bg='#000000', width=screen_width, height=screen_height)
    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2
    image_canvas.create_image(x, y, image=image_photo, anchor=tk.NW)
    image_canvas.pack()
    image_window.update()

def wake_word():

    porcupine = pvporcupine.create(keywords=["Lumina",],
                            access_key=pv_access_key,
                            model_path="/home/pi/.local/lib/python3.9/site-packages/pvporcupine/lib/common/porcupine_params_it.pv",
                            sensitivities=[0.1], #from 0 to 1.0 - a higher number reduces the miss rate at the cost of increased false alarms
                                   )
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    
    wake_pa = pyaudio.PyAudio()

    porcupine_audio_stream = wake_pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)
    
    Detect = True

    while Detect:
        porcupine_pcm = porcupine_audio_stream.read(porcupine.frame_length)
        porcupine_pcm = struct.unpack_from("h" * porcupine.frame_length, porcupine_pcm)

        porcupine_keyword_index = porcupine.process(porcupine_pcm)

        if porcupine_keyword_index >= 0:

            print("\nWake word detected\n")
            current_time()
            porcupine_audio_stream.stop_stream
            porcupine_audio_stream.close()
            porcupine.delete()         
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
            Detect = False

class Recorder(Thread):
    def __init__(self):
        super().__init__()
        self._pcm = list()
        self._is_recording = False
        self._stop = False

    def is_recording(self):
        return self._is_recording

    def run(self):
        self._is_recording = True

        recorder = PvRecorder(device_index=-1, frame_length=512)
        recorder.start()

        while not self._stop:
            self._pcm.extend(recorder.read())
        recorder.stop()

        self._is_recording = False

    def stop(self):
        self._stop = True
        while self._is_recording:
            pass

        return self._pcm

try:

    o = create(
        access_key=pv_access_key,
        model_path="/home/pi/.local/lib/python3.9/site-packages/pvleopard/lib/common/leopard_params_it.pv", 
        )
    
    count = 0

    while True:
     
        try:
            
            if count == 0:
                display_logo()
            else:
                pass
            count = 1
            recorder = Recorder()
            wake_word()
            text_window_func()
            recorder = Recorder()
            recorder.start()
            listen()
            detect_silence()
            transcript, words = o.process(recorder.stop())
            recorder.stop()
            print("You said: " + transcript)
            on_message(transcript, DisplayOn_list, DisplayOff_list, CloseProgram_list, Save_list) 
            image_label = transcript.replace(" ","_")
            recorder.stop()
            o.delete
            recorder = None
        
        except openai.APIError as e:
            global text_var
            text_var.set("There was an API error.\nPlease try again in a few minutes.")
            text_window.update()
            print("\nThere was an API error. Please try again in a few minutes.")
            recorder.stop()
            o.delete
            recorder = None
            sleep(1)

        except openai.RateLimitError as e:
            text_var.set("You have hit your assigned rate limit.")
            text_window.update()
            print("\nYou have hit your assigned rate limit.")
            recorder.stop()
            o.delete
            recorder = None
            break

        except openai.APIConnectionError as e:
            text_var.set("I am having trouble connecting to the API.\nPlease check your network connection\n and then try again.")
            text_window.update()
            print("\nI am having trouble connecting to the API.  Please check your network connection and then try again.")
            recorder.stop()
            o.delete
            recorder = None
            sleep(1)

        except openai.AuthenticationError as e:
            text_var.set("Your OpenAI API key or token is invalid,\nexpired, or revoked.  Please fix this\nissue and then restart my program.")
            text_window.update()
            print("\nYour OpenAI API key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            recorder.stop()
            o.delete
            recorder = None
            break

except KeyboardInterrupt:
    sys.exit("\nExiting Lumina")
