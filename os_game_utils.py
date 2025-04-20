import os
import multiprocessing
import threading
import signal
import time
import json
import pygame
from pathlib import Path

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
        self.high_score_file = "high_scores.json"
        self.score_lock = threading.Lock()
        self.powerup_lock = threading.Lock()
        self.music_thread = None
        self.input_thread = None
        self.collision_thread = None
        self.alien_processes = []
        self.bullet_count = 0
        self.bullet_count_lock = threading.Lock()
        
    def save_high_score(self, score):
        """Save high score to file using file I/O operations"""
        with self.score_lock:
            try:
                print(f"Attempting to save score: {score}")
                print(f"Current working directory: {os.getcwd()}")
                print(f"High score file path: {os.path.abspath(self.high_score_file)}")
                
                scores = []
                if os.path.exists(self.high_score_file):
                    print("High score file exists, loading current scores")
                    with open(self.high_score_file, 'r') as f:
                        scores = json.load(f)
                else:
                    print("High score file does not exist, creating new file")
                
                scores.append(score)
                scores.sort(reverse=True)
                scores = scores[:10]  # Keep only top 10 scores
                
                print(f"Saving scores: {scores}")
                with open(self.high_score_file, 'w') as f:
                    json.dump(scores, f)
                print("Scores saved successfully")
            except Exception as e:
                print(f"Error saving high score: {e}")
                print(f"Error details: {str(e)}")

    def load_high_scores(self):
        """Load high scores from file"""
        with self.score_lock:
            try:
                print(f"Attempting to load high scores from: {os.path.abspath(self.high_score_file)}")
                if os.path.exists(self.high_score_file):
                    with open(self.high_score_file, 'r') as f:
                        scores = json.load(f)
                        print(f"Loaded scores: {scores}")
                        return scores
                else:
                    print("High score file does not exist, returning empty list")
            except Exception as e:
                print(f"Error loading high scores: {e}")
                print(f"Error details: {str(e)}")
            return []

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

    def start_input_thread(self, input_handler):
        """Handle player input in a separate thread"""
        self.input_thread = threading.Thread(target=input_handler)
        self.input_thread.daemon = True
        self.input_thread.start()

    def start_collision_thread(self, collision_handler):
        """Handle collisions in a separate thread"""
        self.collision_thread = threading.Thread(target=collision_handler)
        self.collision_thread.daemon = True
        self.collision_thread.start()

    def create_alien_process(self, alien_data):
        """Create a new process for an alien"""
        process = multiprocessing.Process(target=alien_process, args=(alien_data,))
        process.daemon = True
        process.start()
        self.alien_processes.append(process)
        return process

    def cleanup_processes(self):
        """Clean up all alien processes"""
        for process in self.alien_processes:
            if process.is_alive():
                process.terminate()
        self.alien_processes.clear()

    def decrement_bullet_count(self):
        """Decrement the bullet count in a thread-safe way"""
        with self.bullet_count_lock:
            if self.bullet_count > 0:
                self.bullet_count -= 1
                print(f"Bullet count decremented. Current count: {self.bullet_count}")

    def increment_bullet_count(self):
        """Increment the bullet count in a thread-safe way"""
        with self.bullet_count_lock:
            self.bullet_count += 1
            print(f"Bullet count incremented. Current count: {self.bullet_count}")

    def get_bullet_count(self):
        """Get the current bullet count in a thread-safe way"""
        with self.bullet_count_lock:
            return self.bullet_count

    def reset_bullet_count(self):
        """Reset the bullet count to zero"""
        with self.bullet_count_lock:
            self.bullet_count = 0
            print("Bullet count reset to 0") 