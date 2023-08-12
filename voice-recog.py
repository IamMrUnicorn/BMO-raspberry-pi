import os
import speech_recognition as sr
from fuzzywuzzy import fuzz
from gradio_client import Client
from gtts import gTTS
import random
import time

# Set up Gradio client
client = Client("https://8a050ec6d496eaca5d.gradio.live/")

IDLE_VIDEO = "./Videos/BMO-idle.mp4"
TALKING_VIDEO = "./Videos/BMO-talking.mp4"

responses = {
    "hello": ("Hello! I'm BeeMoe!", ""),
    "im bored": ("who wants to play video games?", ""),
    "what time is it": ("", "./Videos/Adventure-Time-Intro.mp4"),
    "beemo are you a cowboy?": ("", "./Videos/Robot-Cowboy.mp4")
    # ... other responses ...
}


recognizer = sr.Recognizer()

def play_video(video_path, duration=None):
    #"""Play a video using omxplayer for a specified duration."""
    if duration:
        os.system(f"timeout {duration} omxplayer {video_path}")
    else:
        os.system(f"omxplayer {video_path}")

def play_idle_video():
    #"""Continuously play the idle video."""
    while True:
        play_video(IDLE_VIDEO)

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")

def speak_as_bmo():
    result = client.predict(
        0,	# int | float (numeric value between 0 and 2333) in 'Select Speaker/Singer ID:' Slider component
        "",	# str  in 'Add audio's name to the path to the audio file to be processed (default is the correct format example) Remove the path to use an audio from the dropdown list:' Textbox component
        "audios/SIX-CONSOLES.wav",	# str (Option from: ['audios/LowTierGodSpeech.mp3', 'audios/SIX-CONSOLES.wav', 'audios/borrow-a-fry.mp3', 'audios/somegirl.mp3', 'audios/someguy.mp3']) in 'Auto detect audio path and select from the dropdown:' Dropdown component
        5,	# int | float  in 'Transpose (integer, number of semitones, raise by an octave: 12, lower by an octave: -12):' Number component
        "",	# str (filepath or URL to file) in 'F0 curve file (optional). One pitch per line. Replaces the default F0 and pitch modulation:' File component
        "crepe",	# str  in 'Select the pitch extraction algorithm ('pm': faster extraction but lower-quality speech; 'harvest': better bass but extremely slow; 'crepe': better quality but GPU intensive):' Radio component
        "",	# str  in 'Path to the feature index file. Leave blank to use the selected result from the dropdown:' Textbox component
        "./logs/BMO/added_IVF548_Flat_nprobe_1_BMO_v2.index",	# str (Option from: ['./logs/BMO/added_IVF548_Flat_nprobe_1_BMO_v2.index']) in '3. Path to your added.index file (if it didn't automatically find it.)' Dropdown component
        0,	# int | float (numeric value between 0 and 1) in 'Search feature ratio:' Slider component
        0,	# int | float (numeric value between 0 and 7) in 'If >=3: apply median filtering to the harvested pitch results. The value represents the filter radius and can reduce breathiness.' Slider component
        0,	# int | float (numeric value between 0 and 48000) in 'Resample the output audio in post-processing to the final sample rate. Set to 0 for no resampling:' Slider component
        0,	# int | float (numeric value between 0 and 1) in 'Use the volume envelope of the input to replace or mix with the volume envelope of the output. The closer the ratio is to 1, the more the output envelope is used:' Slider component
        0,	# int | float (numeric value between 0 and 0.5) in 'Protect voiceless consonants and breath sounds to prevent artifacts such as tearing in electronic music. Set to 0.5 to disable. Decrease the value to increase protection, but it may reduce indexing accuracy:' Slider component
        1,	# int | float (numeric value between 1 and 512) in 'Mangio-Crepe Hop Length (Only applies to mangio-crepe): Hop length refers to the time it takes for the speaker to jump to a dramatic pitch. Lower hop lengths take more time to infer but are more pitch accurate.' Slider component
        fn_index=8
    )
    print(f"LOOK HERE => {result}")
    audio_url = result[0]   # Adjust this if the structure of result is different.
    os.system(f"wget {audio_url} -O response.mp3")
    os.system("mpg321 response.mp3")

def process_command(command):
    for key, (response_text, response_video) in responses.items():
        if fuzz.partial_ratio(command, key) > 80:
            # Calculate duration based on length of response_text
            duration = len(response_text) * 0.1
            if len(response_video) == 0 :
                response_video = TALKING_VIDEO
            play_video(response_video, duration)
            speak(response_text)
            print()
            speak_as_bmo()
            return
    # If no specific response matches
    speak_as_bmo("What?")
    play_video(TALKING_VIDEO, 2)  # Assuming 2 seconds for a generic "What?" response



# Main loop
try:
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            audio_data = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_data)
                print("You said:", text)
                process_command(text)
            except sr.UnknownValueError:
                print("Sorry mic no worky :(")
except KeyboardInterrupt:
    # Handle Ctrl+C to exit
    print("Exiting...")

# Outside of the while loop, let's run the idle video loop
play_idle_video()

