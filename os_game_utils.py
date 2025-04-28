import os
import multiprocessing
import threading
import signal
import time
import json
import pygame
from pathlib import Path
from game_os_wrapper import GameOSWrapper

def alien_process(alien_data):
    """Process for handling individual alien behavior"""
    while True:
        try:
            # Update alien position and check collisions
            time.sleep(0.016)  # ~60 FPS
        except Exception as e:
            print(f"Error in alien process: {e}")
            break

class GameOSUtils:
    def __init__(self):
        self.game_os = GameOSWrapper()
        self.powerup_lock = threading.Lock()
        self.music_thread = None
        self.input_thread = None
        self.collision_thread = None
        self.alien_processes = []
        self.bullet_count = 0
        self.bullet_count_lock = threading.Lock()
        
    def start_music_thread(self, music_file):
        """Start background music in a separate thread"""
        def play_music():
            try:
                if os.path.exists(music_file):
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.play(-1)  # -1 for infinite loop
                else:
                    print(f"Music file not found: {music_file}. Continuing without background music.")
            except Exception as e:
                print(f"Error playing music: {e}. Continuing without background music.")
        self.music_thread = threading.Thread(target=play_music)
        self.music_thread.daemon = True
        self.music_thread.start()
