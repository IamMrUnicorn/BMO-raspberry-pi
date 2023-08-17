from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.uix.video import Video
from kivy.clock import Clock
import threading

import speech_recognition as sr
from fuzzywuzzy import process
from gtts import gTTS
import os
import random

TALKING_VIDEO = './Videos/BMO-talking.mp4'

responses = {
    "hello": [
        {"response": "hello im bmo", "video": TALKING_VIDEO},
        {"response": "hi there!", "video": TALKING_VIDEO}
    ],
    "what time is it": [
        {"video": "./Videos/Adventure-Time-Intro.mp4"}
    ],
    "hey sing me a song": [
        {"video": TALKING_VIDEO, "audio": "./songs/Fly me to the Moon.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/I Dont Want to Set the World on Fire.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/Rises the Moon.mp3"}
    ],
    "stop": [
        {"response": "Shutting down. Goodbye!"}
    ],
}

image_directory = "./faces"
images = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]

class BMOApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False  # Flag to check if video or audio is currently playing

    def build(self):
        self.layout = BoxLayout()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_interval(self.listen_for_command, 10)  # Check for voice command every 10 seconds
        Clock.schedule_interval(self.change_face, 40)  # Change face every 40 seconds
        return self.layout

    def change_face(self, *args):
        self.image.source = random.choice(images)

    def play_audio(self, audio_path):
        sound = SoundLoader.load(audio_path)
        if sound:
            sound.play()
            sound.bind(on_stop=self.on_audio_end)

    def on_audio_end(self, *args):
        self.is_playing = False

    def listen_for_command(self, *args):
        if self.is_playing:  # If a video or audio is currently playing, don't listen for commands
            return
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)

        try:
            speech_text = r.recognize_google(audio)
            closest_match, score = process.extractOne(speech_text, responses.keys())
            if score >= 80:
                self.process_command(closest_match)
        except sr.UnknownValueError:
            self.speak("I didn't catch that. Can you say it again?")
        except sr.RequestError:
            self.speak("I'm having trouble understanding right now. Please check the connection or try again later.")

    def process_command(self, command):
        self.is_playing = True  # Set the flag to indicate that a video or audio will be playing
        if command == "stop":
            self.speak(responses["stop"][0]["response"])
            self.stop()  # This will stop the Kivy application
            return
        
        response_options = responses[command]
        selected_response = random.choice(response_options)
        if selected_response.get("response"):
            self.speak(selected_response["response"])
        if selected_response.get("video"):
            self.play_video(selected_response["video"])
        if selected_response.get("audio"):
            self.play_audio(selected_response["audio"])

    def play_video(self, video_path):
        self.layout.clear_widgets()  # Clear the current widgets
        video = Video(source=video_path, allow_stretch=True)
        video.bind(eos=self.on_video_end)  # Bind the end-of-stream event
        self.layout.add_widget(video)
        video.state = 'play'  # Change this lin

    def on_video_end(self, *args):
        # This function is called when the video ends
        self.is_playing = False  # Reset the flag
        self.layout.clear_widgets()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_interval(self.listen_for_command, 10)  # Start listening for commands again

    def speak(self, text):
        def play_tts_audio():
            tts = gTTS(text)
            tts.save("temp_audio.mp3")
            os.system("mpg321 temp_audio.mp3")

        threading.Thread(target=play_tts_audio).start()

BMOApp().run()
