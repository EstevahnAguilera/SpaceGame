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
   or if one already exists
   ```
   make clean && make
   ```

   This will compile `game_os.c` into a shared library `libgame_os.so` that the Python game uses.

5. Run the game:
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

   There are three main threads that are being used in the program:
   1. Main Game Thread (Python):
      - The main thread running alien_invasion.py
      - Handles pygame display, user input, and rendering
      - Runs the main game loop in run_game()
   2. Game Logic Thread (C):
      - Created by pthread_create(&game_logic_thread, NULL, game_logic_loop, NULL)
      - Handles game state updates, physics, collisions
      - Runs at 60 FPS
   3. Music Thread (Python):
      - Created in GameOSUtils.start_music_thread():
      - We do this Python since PyGame abstracts away the sound so we can focus on the core game logic using C.

   Example: In `game_os.c`, a game logic thread is created to handle game state updates, allowing these operations to run concurrently without blocking the main game thread that is running in Python.

   Screenshot of pthread being created for the game logic loop:

   <img width="385" alt="image" src="https://github.com/user-attachments/assets/64e7a82a-93ef-47da-9cfe-b3c2d94b9cbc" />


3. **Synchronization (Mutex)**
   The game uses mutex locks to protect shared resources and prevent race conditions. The game state structure includes mutexes to ensure thread-safe access to critical data like player position, score, and game status.

   Example: The `GameState` structure in `game_os.c` includes a `pthread_mutex_t mutex` that protects critical sections when updating player position or game state. This ensures that only one thread can modify shared data at a time.

   Screenshot of several functions making use of Mutex for protection:

   <img width="417" alt="image" src="https://github.com/user-attachments/assets/98e54725-c3c4-4c75-a619-31b31e267405" />


4. **File Management**
   The game implements file operations for persistent storage of high scores. The Python layer handles file I/O operations with proper error handling and synchronization to ensure data consistency.

   Example: In `os_game_utils.py`, the `save_high_score()` and `load_high_scores()` methods use file operations to store and retrieve high scores. These operations are protected by a mutex lock to prevent race conditions when multiple threads try to access the high score file simultaneously.

   Screenshot of `save_high_score()` and its use of file management:
   
   <img width="351" alt="image" src="https://github.com/user-attachments/assets/eaafc8e6-901c-4e61-ba60-35b3de80660c" />


6. **Shared Memory**
   - Used for thread communication within the same process. In this case, the shared memory is so that the Python main thread can access the memory created by the game logic thread in C.
   
   - Basically, whenever a user enters input, PyGame and Python capture the users input then sends it via the shared memory segement called `game_state` to the core game logic thread running in C. C does its computations and updates the variables stored within this `game_state` shared memory segment. PyGame and Python then read the variables in the `game_state` shared memory segment and update the graphics to reflect the changes in positions that the threads in C calculated previously.
  
      - The `GlobalGameState` structure holds all shared game state:
      ```c
      typedef struct {
            GameState game_state;
            Alien aliens[MAX_ALIENS];
            Bullet bullets[100];
            int num_aliens;
            int num_bullets;
            // ... other game state
      } GlobalGameState;
      ```
      - Protected by mutex locks to ensure thread-safe access
      - Allows the main thread (the Python process) and game logic thread to communicate through shared state

   Example #2:
   - When the game starts, the C layer creates a shared memory segment using `shmget()`
   - This shared memory segment (`GlobalGameState`) holds all game state including:
     - Player position and health
     - Alien positions and states
     - Bullet positions and states
     - Game status (active/over)
   - Screenshot proof of shared memory being used within the game:

     <img width="365" alt="image" src="https://github.com/user-attachments/assets/b096adf8-f9f1-4683-9025-16fce67d3c6c" />


7. **Memory Management**
   The game demonstrates several memory management concepts:
   
   a) **Static Memory Allocation**
   - Fixed-size arrays for game entities:
     ```c
     Alien aliens[MAX_ALIENS];  // Array for aliens
     Bullet bullets[100];       // Array for bullets
     ```
   - This approach provides predictable memory usage and prevents fragmentation

   b) **Dynamic Memory Management**
   - Memory allocation and cleanup:
     ```c
     // Allocation
     game_state = (GlobalGameState*)shmat(shm_id, NULL, 0);
     ```
   - Screenshot of `init_game_state()` being used for the memory management of the shared memory (initialization)
     
   <img width="442" alt="image" src="https://github.com/user-attachments/assets/87df41a9-4868-4310-8819-2b5be716b3c3" />

   - Screenshot of `cleanup()` being used for the memory management of the shared memory (cleanup)
     
   <img width="378" alt="image" src="https://github.com/user-attachments/assets/56e975af-ddab-4e96-8332-a3f16aad7aa9" />

   - Memory initialization:
     ```c
     memset(game_state, 0, sizeof(GlobalGameState));
     ```

## What's Next  
Here's what we're planning to add before the final version:
- Better scoring system, with visible score updates  
- Increasing alien speed as difficulty ramps up  
- Random power-ups to make things more exciting  
- Sound effects and visual feedback for hits and explosions  
- A high score system to track the best players  
