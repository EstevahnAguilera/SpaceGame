#ifndef GAME_OS_H
#define GAME_OS_H

#include <sys/types.h>
#include <pthread.h>

// Initialize game state and shared memory
int init_game_state();

// Start the game
void start_game();

// Game logic functions
void update_player_movement(int left, int right, int up, int down);
void fire_player_bullet();

// Get game state
void get_game_state(int* player_x, int* player_y, int* player_health, 
                   int* score, int* game_active, int* game_over);

// Get positions for rendering
void get_alien_positions(int* positions, int* count);
void get_bullet_positions(int* positions, int* count);

// Level management
void get_level(int* level);
void advance_level();

// Cleanup resources
void cleanup();

// File management functions
void save_high_score(int score);
void load_high_scores(int* scores, int* count);

#endif // GAME_OS_H 