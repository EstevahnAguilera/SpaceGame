#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <math.h>

// Game constants
#define MAX_ALIENS 50
#define ALIEN_SPEED 2
#define BULLET_SPEED 5
#define SCREEN_WIDTH 1200
#define SCREEN_HEIGHT 800
#define SHIP_SPEED 5

// File management functions
#define HIGH_SCORE_FILE "high_scores.json"
#define MAX_HIGH_SCORES 10

// Shared memory structure for game state
typedef struct {
    int player_x;
    int player_y;
    int player_health;
    int score;
    int game_active;
    int game_over;
    int player_moving_left;
    int player_moving_right;
    int player_moving_up;
    int player_moving_down;
    pthread_mutex_t mutex;
} GameState;

// Structure for alien
typedef struct {
    int x;
    int y;
    int health;
    int active;
    int direction;  // 1 for right, -1 for left
} Alien;

// Structure for bullet
typedef struct {
    int x;
    int y;
    int active;
    int is_player_bullet;
} Bullet;

// Global game state
typedef struct {
    GameState game_state;
    Alien aliens[MAX_ALIENS];
    Bullet bullets[100];  // Max 100 bullets
    int num_aliens;
    int num_bullets;
    int alien_direction;  // Fleet direction
    int fleet_drop_speed;
} GlobalGameState;

// Global variables
static GlobalGameState* game_state = NULL;
static int shm_id;
static pthread_t game_logic_thread;
static int thread_running = 0;

// Structure for high scores
typedef struct {
    int scores[MAX_HIGH_SCORES];
    int count;
} HighScores;

// Initialize shared memory and game state
int init_game_state() {
    // Create shared memory segment
    shm_id = shmget(IPC_PRIVATE, sizeof(GlobalGameState), IPC_CREAT | 0666);
    if (shm_id == -1) {
        perror("shmget");
        return -1;
    }

    // Attach shared memory
    game_state = (GlobalGameState*)shmat(shm_id, NULL, 0);
    if (game_state == (void*)-1) {
        perror("shmat");
        return -1;
    }

    // Initialize mutex
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutex_init(&game_state->game_state.mutex, &attr);

    // Initialize game state
    memset(game_state, 0, sizeof(GlobalGameState));
    game_state->game_state.player_x = SCREEN_WIDTH / 2;
    game_state->game_state.player_y = SCREEN_HEIGHT - 50;
    game_state->game_state.player_health = 100;
    game_state->game_state.score = 0;
    game_state->game_state.game_active = 0;
    game_state->game_state.game_over = 0;
    game_state->alien_direction = 1;
    game_state->fleet_drop_speed = 10;

    return 0;
}

// Game logic thread function
void* game_logic_loop(void* arg) {
    while (thread_running) {
        pthread_mutex_lock(&game_state->game_state.mutex);
        
        if (game_state->game_state.game_active) {
            // Update player position based on movement flags
            if (game_state->game_state.player_moving_left && 
                game_state->game_state.player_x > 0) {
                game_state->game_state.player_x -= SHIP_SPEED;
            }
            if (game_state->game_state.player_moving_right && 
                game_state->game_state.player_x < SCREEN_WIDTH - 50) {
                game_state->game_state.player_x += SHIP_SPEED;
            }
            if (game_state->game_state.player_moving_up && 
                game_state->game_state.player_y > 0) {
                game_state->game_state.player_y -= SHIP_SPEED;
            }
            if (game_state->game_state.player_moving_down && 
                game_state->game_state.player_y < SCREEN_HEIGHT - 50) {
                game_state->game_state.player_y += SHIP_SPEED;
            }

            // Update alien positions
            for (int i = 0; i < game_state->num_aliens; i++) {
                if (game_state->aliens[i].active) {
                    game_state->aliens[i].x += ALIEN_SPEED * game_state->alien_direction;
                    
                    // Check fleet edges
                    if (game_state->aliens[i].x <= 0 || 
                        game_state->aliens[i].x >= SCREEN_WIDTH - 30) {
                        game_state->alien_direction *= -1;
                        for (int j = 0; j < game_state->num_aliens; j++) {
                            if (game_state->aliens[j].active) {
                                game_state->aliens[j].y += game_state->fleet_drop_speed;
                            }
                        }
                        break;
                    }
                }
            }

            // Update bullet positions
            for (int i = 0; i < game_state->num_bullets; i++) {
                if (game_state->bullets[i].active) {
                    if (game_state->bullets[i].is_player_bullet) {
                        game_state->bullets[i].y -= BULLET_SPEED;
                    } else {
                        game_state->bullets[i].y += BULLET_SPEED;
                    }

                    // Remove bullets that are off screen
                    if (game_state->bullets[i].y < 0 || 
                        game_state->bullets[i].y > SCREEN_HEIGHT) {
                        game_state->bullets[i].active = 0;
                    }
                }
            }

            // Check collisions
            for (int i = 0; i < game_state->num_bullets; i++) {
                if (!game_state->bullets[i].active) continue;

                if (game_state->bullets[i].is_player_bullet) {
                    // Check player bullet-alien collisions
                    for (int j = 0; j < game_state->num_aliens; j++) {
                        if (!game_state->aliens[j].active) continue;

                        if (abs(game_state->bullets[i].x - game_state->aliens[j].x) < 30 &&
                            abs(game_state->bullets[i].y - game_state->aliens[j].y) < 30) {
                            game_state->bullets[i].active = 0;
                            game_state->aliens[j].active = 0;
                            game_state->game_state.score += 10;
                            break;
                        }
                    }
                } else {
                    // Check alien bullet-player collisions
                    if (abs(game_state->bullets[i].x - game_state->game_state.player_x) < 30 &&
                        abs(game_state->bullets[i].y - game_state->game_state.player_y) < 30) {
                        game_state->game_state.player_health -= 10;
                        game_state->bullets[i].active = 0;
                        
                        if (game_state->game_state.player_health <= 0) {
                            game_state->game_state.game_active = 0;
                            game_state->game_state.game_over = 1;
                        }
                    }
                }
            }

            // Random alien shooting
            if (rand() % 100 < 2) {  // 2% chance per frame
                for (int i = 0; i < game_state->num_aliens; i++) {
                    if (game_state->aliens[i].active && rand() % 10 == 0) {
                        if (game_state->num_bullets < 100) {
                            game_state->bullets[game_state->num_bullets].x = game_state->aliens[i].x;
                            game_state->bullets[game_state->num_bullets].y = game_state->aliens[i].y;
                            game_state->bullets[game_state->num_bullets].active = 1;
                            game_state->bullets[game_state->num_bullets].is_player_bullet = 0;
                            game_state->num_bullets++;
                        }
                    }
                }
            }
        }
        
        pthread_mutex_unlock(&game_state->game_state.mutex);
        usleep(16667);  // ~60 FPS
    }
    return NULL;
}

// Start the game
void start_game() {
    pthread_mutex_lock(&game_state->game_state.mutex);
    game_state->game_state.game_active = 1;
    game_state->game_state.game_over = 0;
    game_state->game_state.player_health = 100;
    game_state->game_state.score = 0;
    
    // Create initial fleet
    game_state->num_aliens = 0;
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 6; x++) {
            if (game_state->num_aliens < MAX_ALIENS) {
                game_state->aliens[game_state->num_aliens].x = 100 + x * 80;
                game_state->aliens[game_state->num_aliens].y = 50 + y * 60;
                game_state->aliens[game_state->num_aliens].health = 100;
                game_state->aliens[game_state->num_aliens].active = 1;
                game_state->num_aliens++;
            }
        }
    }
    pthread_mutex_unlock(&game_state->game_state.mutex);

    // Start game logic thread if not already running
    if (!thread_running) {
        thread_running = 1;
        pthread_create(&game_logic_thread, NULL, game_logic_loop, NULL);
    }
}

// Update player movement flags
void update_player_movement(int left, int right, int up, int down) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    game_state->game_state.player_moving_left = left;
    game_state->game_state.player_moving_right = right;
    game_state->game_state.player_moving_up = up;
    game_state->game_state.player_moving_down = down;
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Fire player bullet
void fire_player_bullet() {
    pthread_mutex_lock(&game_state->game_state.mutex);
    if (game_state->num_bullets < 100) {
        game_state->bullets[game_state->num_bullets].x = game_state->game_state.player_x;
        game_state->bullets[game_state->num_bullets].y = game_state->game_state.player_y;
        game_state->bullets[game_state->num_bullets].active = 1;
        game_state->bullets[game_state->num_bullets].is_player_bullet = 1;
        game_state->num_bullets++;
    }
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Get game state
void get_game_state(int* player_x, int* player_y, int* player_health, 
                   int* score, int* game_active, int* game_over) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    *player_x = game_state->game_state.player_x;
    *player_y = game_state->game_state.player_y;
    *player_health = game_state->game_state.player_health;
    *score = game_state->game_state.score;
    *game_active = game_state->game_state.game_active;
    *game_over = game_state->game_state.game_over;
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Get alien positions
void get_alien_positions(int* positions, int* count) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    *count = game_state->num_aliens;
    for (int i = 0; i < game_state->num_aliens; i++) {
        positions[i * 3] = game_state->aliens[i].x;
        positions[i * 3 + 1] = game_state->aliens[i].y;
        positions[i * 3 + 2] = game_state->aliens[i].active;
    }
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Get bullet positions
void get_bullet_positions(int* positions, int* count) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    *count = game_state->num_bullets;
    for (int i = 0; i < game_state->num_bullets; i++) {
        positions[i * 4] = game_state->bullets[i].x;
        positions[i * 4 + 1] = game_state->bullets[i].y;
        positions[i * 4 + 2] = game_state->bullets[i].is_player_bullet;
        positions[i * 4 + 3] = game_state->bullets[i].active;
    }
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Handle alien hit by bullet
void handle_alien_hit(int alien_x, int alien_y) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    
    // Find and deactivate the alien
    for (int i = 0; i < game_state->num_aliens; i++) {
        if (game_state->aliens[i].active && 
            abs(game_state->aliens[i].x - alien_x) < 30 &&
            abs(game_state->aliens[i].y - alien_y) < 30) {
            game_state->aliens[i].active = 0;
            game_state->game_state.score += 10;
            break;
        }
    }
    
    // Find and deactivate any bullets that hit this alien
    for (int i = 0; i < game_state->num_bullets; i++) {
        if (game_state->bullets[i].active && 
            abs(game_state->bullets[i].x - alien_x) < 30 &&
            abs(game_state->bullets[i].y - alien_y) < 30) {
            game_state->bullets[i].active = 0;
        }
    }
    
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Save high score to file
void save_high_score(int score) {
    FILE* file = fopen(HIGH_SCORE_FILE, "r");
    HighScores high_scores = {0};
    
    // Read existing scores if file exists
    if (file) {
        char buffer[1024];
        size_t len = fread(buffer, 1, sizeof(buffer), file);
        fclose(file);
        
        if (len > 0) {
            buffer[len] = '\0';
            char* token = strtok(buffer, "[], ");
            while (token && high_scores.count < MAX_HIGH_SCORES) {
                high_scores.scores[high_scores.count++] = atoi(token);
                token = strtok(NULL, "[], ");
            }
        }
    }
    
    // Add new score
    if (high_scores.count < MAX_HIGH_SCORES) {
        high_scores.scores[high_scores.count++] = score;
    } else if (score > high_scores.scores[MAX_HIGH_SCORES - 1]) {
        high_scores.scores[MAX_HIGH_SCORES - 1] = score;
    }
    
    // Sort scores in descending order
    for (int i = 0; i < high_scores.count - 1; i++) {
        for (int j = i + 1; j < high_scores.count; j++) {
            if (high_scores.scores[i] < high_scores.scores[j]) {
                int temp = high_scores.scores[i];
                high_scores.scores[i] = high_scores.scores[j];
                high_scores.scores[j] = temp;
            }
        }
    }
    
    // Write scores back to file
    file = fopen(HIGH_SCORE_FILE, "w");
    if (file) {
        fprintf(file, "[");
        for (int i = 0; i < high_scores.count; i++) {
            fprintf(file, "%d", high_scores.scores[i]);
            if (i < high_scores.count - 1) {
                fprintf(file, ", ");
            }
        }
        fprintf(file, "]");
        fclose(file);
    }
}

// Load high scores from file
void load_high_scores(int* scores, int* count) {
    FILE* file = fopen(HIGH_SCORE_FILE, "r");
    *count = 0;
    
    if (file) {
        char buffer[1024];
        size_t len = fread(buffer, 1, sizeof(buffer), file);
        fclose(file);
        
        if (len > 0) {
            buffer[len] = '\0';
            char* token = strtok(buffer, "[], ");
            while (token && *count < MAX_HIGH_SCORES) {
                scores[*count] = atoi(token);
                (*count)++;
                token = strtok(NULL, "[], ");
            }
        }
    }
}

// Cleanup function
void cleanup() {
    thread_running = 0;
    if (game_state != NULL) {
        pthread_mutex_destroy(&game_state->game_state.mutex);
        shmdt(game_state);
        shmctl(shm_id, IPC_RMID, NULL);
    }
} 