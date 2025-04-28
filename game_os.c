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
#include <signal.h>

// Game constants
#define MAX_ALIENS 50
#define BULLET_SPEED 10
#define ALIEN_BULLET_SPEED 5  // Increased from 5
#define SCREEN_WIDTH 1200
#define SCREEN_HEIGHT 800
#define SHIP_SPEED 5

// Shooting frequency constants
#define ALIEN_SHOOT_CHANCE 5    // Base chance per frame (out of 100). Controls the base chance of shooting per frame (currently 5%)
#define ALIEN_SHOOT_DIVISOR 5   // Per-alien chance (1 out of this number)

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
    int level;  // Add level tracking
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
    float alien_speed;  // Add alien speed as a variable
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

// Cleanup function declaration
void cleanup();

// Signal handler for cleanup
static void signal_handler(int signum) {
    cleanup();
    exit(0);
}

// Initialize shared memory and game state
int init_game_state() {
    // Set up signal handlers
    signal(SIGINT, signal_handler);   // Ctrl+C
    signal(SIGTERM, signal_handler);  // Termination signal
    signal(SIGSEGV, signal_handler);  // Segmentation fault
    
    // First try to clean up any existing shared memory
    if (game_state != NULL) {
        pthread_mutex_destroy(&game_state->game_state.mutex);
        shmdt(game_state);
        shmctl(shm_id, IPC_RMID, NULL);
        game_state = NULL;
    }

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
        shmctl(shm_id, IPC_RMID, NULL);
        return -1;
    }

    // Initialize mutex
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    if (pthread_mutex_init(&game_state->game_state.mutex, &attr) != 0) {
        perror("pthread_mutex_init");
        shmdt(game_state);
        shmctl(shm_id, IPC_RMID, NULL);
        game_state = NULL;
        return -1;
    }

    // Initialize game state
    memset(game_state, 0, sizeof(GlobalGameState));
    game_state->game_state.player_x = SCREEN_WIDTH / 2;
    game_state->game_state.player_y = SCREEN_HEIGHT - 50;
    game_state->game_state.player_health = 100;
    game_state->game_state.score = 0;
    game_state->game_state.game_active = 0;
    game_state->game_state.game_over = 0;
    game_state->game_state.level = 1;  // Initialize level
    game_state->alien_direction = 1;
    game_state->fleet_drop_speed = 10;
    game_state->alien_speed = 2.0;  // Initialize alien speed

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
                    game_state->aliens[i].x += game_state->alien_speed * game_state->alien_direction;
                    
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

            // Update bullet positions and cleanup inactive bullets
            int active_bullets = 0;
            for (int i = 0; i < game_state->num_bullets; i++) {
                if (game_state->bullets[i].active) {
                    if (game_state->bullets[i].is_player_bullet) {
                        game_state->bullets[i].y -= BULLET_SPEED;
                    } else {
                        game_state->bullets[i].y += ALIEN_BULLET_SPEED;  // Use faster speed for alien bullets
                    }

                    // Remove bullets that are off screen
                    if (game_state->bullets[i].y < 0 || 
                        game_state->bullets[i].y > SCREEN_HEIGHT) {
                        game_state->bullets[i].active = 0;
                    } else {
                        active_bullets++;
                    }
                }
            }

            // Compact bullet array by moving active bullets to the front
            int write_index = 0;
            for (int i = 0; i < game_state->num_bullets; i++) {
                if (game_state->bullets[i].active) {
                    if (write_index != i) {
                        game_state->bullets[write_index] = game_state->bullets[i];
                    }
                    write_index++;
                }
            }
            game_state->num_bullets = active_bullets;

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

            // Random alien shooting - increased frequency
            if (rand() % 100 < ALIEN_SHOOT_CHANCE) {  // Use constant
                for (int i = 0; i < game_state->num_aliens; i++) {
                    if (game_state->aliens[i].active && rand() % ALIEN_SHOOT_DIVISOR == 0) {  // Use constant
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
    game_state->game_state.level = 1;  // Reset level
    
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

// Add new function to get level
void get_level(int* level) {
    pthread_mutex_lock(&game_state->game_state.mutex);
    *level = game_state->game_state.level;
    pthread_mutex_unlock(&game_state->game_state.mutex);
}

// Add new function to advance level
__attribute__((visibility("default"))) void advance_level() {
    pthread_mutex_lock(&game_state->game_state.mutex);
    game_state->game_state.level++;
    
    // Increase difficulty more gradually
    game_state->fleet_drop_speed += 1;  // Reduced from 2 - aliens move slightly faster
    game_state->alien_speed += 0.2;     // Reduced from 0.5 - aliens move slightly faster horizontally
    
    // Create new fleet
    game_state->num_aliens = 0;
    int rows = 3 + (game_state->game_state.level - 1);  // Add one more row per level
    int cols = 6 + (game_state->game_state.level - 1);  // Add one more column per level
    
    for (int y = 0; y < rows; y++) {
        for (int x = 0; x < cols; x++) {
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
}

// Cleanup function
void cleanup() {
    // Stop the game logic thread
    thread_running = 0;
    
    // Wait for the game logic thread to finish
    if (game_state != NULL) {
        pthread_join(game_logic_thread, NULL);
        
        // Clean up shared memory
        pthread_mutex_destroy(&game_state->game_state.mutex);
        shmdt(game_state);
        shmctl(shm_id, IPC_RMID, NULL);
        game_state = NULL;
    }
    
    // Reset global variables
    thread_running = 0;
    shm_id = 0;
} 