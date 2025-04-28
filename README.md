# Alien Invasion - Space Invaders Clone

# Contributers
- Nathan Pader
- Raymond Lee
- Siba Filipovic
- Estevahn Aguilera

## Demo Video  
[YouTube Demo Link](https://youtu.be/OggmmaCZkrM)

## Installation and Setup

1. First, create and activate a Python virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # .\venv\Scripts\activate
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Compile the C code:
   ```bash
   # Using the provided Makefile
   make
   ```
   This will compile `game_os.c` into a shared library `libgame_os.so` that the Python game uses.

4. Run the game:
   ```bash
   python alien_invasion.py
   ```

## Notes
- Make sure you have Python 3.x installed
- The C code compilation requires gcc to be installed
- The game requires the compiled `libgame_os.so` to run properly

## Game Overview

### Game Title  
Alien Invasion

### Game Summary  
Alien Invasion is a simple top-down arcade shooter inspired by the classic *Space Invaders*. You control a spaceship that slides left and right along the bottom of the screen. Your job is to shoot down waves of aliens before they reach you. If you destroy them all, the game starts a new wave and keeps going. It's fast, fun, and we're using it as a creative way to explore operating system concepts through gameplay.

As of now, the game is work in progress. We hope to implement a fun user experience with sounds and dynamic gameplay that makes the game progressively challenging while implementing more operating systems concepts.

### Core Gameplay Loop  
- Move your ship using the arrow keys  
- Shoot bullets to take down aliens  
- Try to clear each wave before the aliens get too close  
- Repeat and survive as long as you can  

## Gameplay Mechanics

### Controls  
- Left Arrow / Right Arrow: Move the ship  
- Spacebar: Fire bullets  
- Mouse Click: Start the game from the main menu  

### Core Mechanics  
- You can shoot, but only a few bullets at a time  
- Aliens move as a group and bounce across the screen  
- Bullets disappear when they hit an alien or leave the screen  
- Aliens speed up over time to increase difficulty  

### Level Progression  
Each time you clear a wave of aliens, a new one spawns. The new wave might move faster or have new behaviors to keep things interesting.

### Win/Loss Conditions  
- You win each round by clearing all the aliens  
- You lose if any alien reaches the bottom or crashes into your ship  

## Story and Narrative  
There isn't an interactive storyline yet as the focus of the game is on arcade-style gameplay. Here is the backstory though:

There was once a man named Bob.

Adrift in the endless abyss of deep space, he was at peace after a life of endless conflict relaxing in his Arc280 Space Fighter. He was one of few surviving veterans of the Great Mars Incursion 60 years prior where an Alien Hegemony invaded the Solar System and nearly wiped out mankind. Just 20 years old at the time of the conflict, Bob joined the United Nations Space Core and quickly rose up the ranks to become the Grand Sea Lord of the UN Space Core. As the chief naval commander for all humankind, he commanded a decisive battle that vanguished the Alien Hegemony. Bob was honored as a war hero and lives on as a living legend.

Back on the Arc, Bob sipped on his coffee before it slipped out of his hand and shattered into thousands of pieces on the ground. As Bob gazed out of his ship, he once thought he'll never have to see war again, but here he is now 82 old seeing a endless horde of Alien spacecraft closing in fast.

Bob sighs. At first, he is stunned, but as his feable 80 year old frame almost creaks as he mounts the seat to his nearly obsolete and decommissioned Arc Space Fighter. 

Bob may be outnumbered, but as he is approached by thousands of Aliens ahead, he cracks his knuckles; he grins. He was at peace but rather bored on the Arc, but now he'll once again be able to have some fun.


## OS Concepts Used

The game implements a hybrid architecture where PyGame and Python handle the graphics rendering and input processing, while the core game logic is implemented in C. This implementation allows us to demonstrate several key operating system concepts while abstracting complicated graphics to PyGame. Here's how the system works:

The game uses a hybrid architecture where Python and C work together in a coordinated pipeline:
- PyGame captures user input (keyboard/mouse events)
- Python processes these events and calls the appropriate C functions through the `GameOSWrapper` interface
- The C layer computes new positions and game state based on the input
- The updated state is sent back to Python
- PyGame renders the new positions and game state

Example: When a player presses the left arrow key:
1. PyGame detects the key press event
2. Python's `GameOSWrapper` calls `update_player_movement(1, 0, 0, 0)` to signal left movement
3. The C layer (`game_os.c`) updates the player's position in shared memory
4. Python retrieves the new position through `get_game_state()`
5. PyGame renders the ship at the new position

This demonstrates how different processes can work together in a coordinated manner, with each layer handling specific responsibilities:
- PyGame: Input capture and graphics rendering
- Python: Event handling and C interface
- C: Core game logic and state management

1. **Threading**
   The C implementation uses pthreads to handle concurrent operations. Multiple threads are used to manage different aspects of the game simultaneously, such as alien movement, collision detection, and game state updates.

   Example: In `game_os.c`, separate threads are created to handle alien movement and game state updates, allowing these operations to run concurrently without blocking the main game loop.

2. **Synchronization (Mutex)**
   The game uses mutex locks to protect shared resources and prevent race conditions. The game state structure includes mutexes to ensure thread-safe access to critical data like player position, score, and game status.

   Example: The `GameState` structure in `game_os.c` includes a `pthread_mutex_t mutex` that protects critical sections when updating player position or game state. This ensures that only one thread can modify shared data at a time.

3. **File Management**
   The game implements file operations for persistent storage of high scores. The Python layer handles file I/O operations with proper error handling and synchronization to ensure data consistency.

   Example: In `os_game_utils.py`, the `save_high_score()` and `load_high_scores()` methods use file operations to store and retrieve high scores. These operations are protected by a mutex lock to prevent race conditions when multiple threads try to access the high score file simultaneously.

4. **Shared Memory + Memory Management**
   The game demonstrates efficient memory management through the use of shared memory segments and careful allocation of game objects. The C layer manages memory for game entities (aliens, bullets) while providing controlled access through well-defined interfaces.

   Example #1: The `GlobalGameState` structure in `game_os.c` pre-allocates arrays for aliens and bullets, with fixed maximum sizes. This approach prevents memory fragmentation and provides predictable memory usage patterns.

   Example #2:
   - When the game starts, the C layer creates a shared memory segment using `shmget()`
   - This shared memory segment (`GlobalGameState`) holds all game state including:
     - Player position and health
     - Alien positions and states
     - Bullet positions and states
     - Game status (active/over)
   - Example from `game_os.c`:
     ```c
     int init_game_state() {
         // Create shared memory segment
         shm_id = shmget(IPC_PRIVATE, sizeof(GlobalGameState), IPC_CREAT | 0666);
         // Attach shared memory
         game_state = (GlobalGameState*)shmat(shm_id, NULL, 0);
         // Initialize mutex for thread safety
         pthread_mutex_init(&game_state->game_state.mutex, &attr);
     }
     ```

## What's Next  
Here's what we're planning to add before the final version:
- Better scoring system, with visible score updates  
- Increasing alien speed as difficulty ramps up  
- Random power-ups to make things more exciting  
- Sound effects and visual feedback for hits and explosions  
- A high score system to track the best players  
