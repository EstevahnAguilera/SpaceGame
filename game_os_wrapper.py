import ctypes
import os
from ctypes import c_int, c_void_p, POINTER

class GameOSWrapper:
    def __init__(self):
        # Load the shared library
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, 'libgame_os.so')
        self.lib = ctypes.CDLL(lib_path)
        
        # Define function prototypes
        self.lib.init_game_state.restype = c_int
        self.lib.init_game_state.argtypes = []
        
        self.lib.start_game.argtypes = []
        
        self.lib.update_player_movement.argtypes = [c_int, c_int, c_int, c_int]
        self.lib.fire_player_bullet.argtypes = []
        
        self.lib.get_game_state.argtypes = [
            POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int)
        ]
        
        self.lib.get_alien_positions.argtypes = [POINTER(c_int), POINTER(c_int)]
        self.lib.get_bullet_positions.argtypes = [POINTER(c_int), POINTER(c_int)]
        
        self.lib.cleanup.argtypes = []
        
        # Add file management function prototypes
        self.lib.save_high_score.argtypes = [c_int]
        self.lib.load_high_scores.argtypes = [POINTER(c_int), POINTER(c_int)]
        
        # Initialize game state
        if self.lib.init_game_state() != 0:
            raise RuntimeError("Failed to initialize game state")
    
    def start_game(self):
        self.lib.start_game()
    
    def update_player_movement(self, left, right, up, down):
        self.lib.update_player_movement(left, right, up, down)
    
    def fire_player_bullet(self):
        self.lib.fire_player_bullet()
    
    def get_game_state(self):
        player_x = c_int()
        player_y = c_int()
        player_health = c_int()
        score = c_int()
        game_active = c_int()
        game_over = c_int()
        
        self.lib.get_game_state(
            ctypes.byref(player_x),
            ctypes.byref(player_y),
            ctypes.byref(player_health),
            ctypes.byref(score),
            ctypes.byref(game_active),
            ctypes.byref(game_over)
        )
        
        return {
            'player_x': player_x.value,
            'player_y': player_y.value,
            'player_health': player_health.value,
            'score': score.value,
            'game_active': bool(game_active.value),
            'game_over': bool(game_over.value)
        }
    
    def get_alien_positions(self):
        """Get positions of all aliens from C"""
        positions = (ctypes.c_int * (50 * 3))()  # MAX_ALIENS * 3 (x, y, active)
        count = ctypes.c_int()
        self.lib.get_alien_positions(positions, ctypes.byref(count))
        result = []
        for i in range(count.value):
            x = positions[i * 3]
            y = positions[i * 3 + 1]
            active = positions[i * 3 + 2]
            result.append((x, y, active))
        return result
    
    def get_bullet_positions(self):
        """Get positions of all bullets from C"""
        positions = (ctypes.c_int * (100 * 4))()  # Max 100 bullets * 4 (x, y, is_player, active)
        count = ctypes.c_int()
        self.lib.get_bullet_positions(positions, ctypes.byref(count))
        result = []
        for i in range(count.value):
            x = positions[i * 4]
            y = positions[i * 4 + 1]
            is_player = positions[i * 4 + 2]
            active = positions[i * 4 + 3]
            result.append((x, y, is_player, active))
        return result
    
    def cleanup(self):
        self.lib.cleanup()

    def save_high_score(self, score):
        """Save high score using C implementation"""
        self.lib.save_high_score(score)

    def load_high_scores(self):
        """Load high scores using C implementation"""
        scores = (c_int * 10)()  # Array of 10 integers
        count = c_int()
        self.lib.load_high_scores(scores, ctypes.byref(count))
        return [scores[i] for i in range(count.value)] 