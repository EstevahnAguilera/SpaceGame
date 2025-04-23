# Alien Invasion - Space Invaders Clone

# Contributers
- Nathan Pader
- Raymond Lee
- Siba Filipovic
- Estevahn Aguilera

## Demo Video  
[YouTube Demo Link](https://youtu.be/OggmmaCZkrM)

## Setup

### Requirements
To run the game, you’ll need:
- Python 3.8 or higher
- The `pygame` library (we also use `multiprocessing` and `threading`)
- It should work on most platforms including Windows, macOS, or Linux

### How to Run
1. First, install the required dependencies:
2. Then just run the game like this:
   ```bash
   python alien_invasion.py
   ```

## Game Overview

### Game Title  
Alien Invasion

### Game Summary  
Alien Invasion is a simple top-down arcade shooter inspired by the classic *Space Invaders*. You control a spaceship that slides left and right along the bottom of the screen. Your job is to shoot down waves of aliens before they reach you. If you destroy them all, the game starts a new wave and keeps going. It’s fast, fun, and we’re using it as a creative way to explore operating system concepts through gameplay.

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
There isn’t an interactive storyline yet as the focus of the game is on arcade-style gameplay.

There was once a man named Bob.

Adrift in the endless abyss of deep space, he was at peace after a life of endless conflict relaxing in his Arc280 Space Fighter. He was one of few surviving veterans of the Great Mars Incursion 60 years prior where an Alien Hegemony invaded the Solar System and nearly wiped out mankind. Just 20 years old at the time of the conflict, Bob joined the United Nations Space Core and quickly rose up the ranks to become the Grand Sea Lord of the UN Space Core. As the chief naval commander for all humankind, he commanded a decisive battle that vanguished the Alien Hegemony. Bob was honored as a war hero and lives on as a living legend.

Back on the Arc, Bob sipped on his coffee before it slipped out of his hand and shattered into thousands of pieces on the ground. As Bob gazed out of his ship, he once thought he'll never have to see war again, but here he is now 82 old seeing a endless horde of Alien spacecraft closing in fast.

Bob sighs. At first, he is stunned, but as his feable 80 year old frame almost creaks as he mounts the seat to his nearly obsolete and decommissioned Arc Space Fighter. 

Bob may be outnumbered, but as he is approached by thousands of Aliens ahead, he cracks his knuckles; he grins. He was at peace but rather bored on the Arc, but now he'll once again be able to have some fun.


## OS Concepts Used

OS concepts are still work in progress. We focused on completing the core gameplay mechanics themselves and are now working on integrating OS concepts within it. We currently have process creations and threading at the moment, with IPC, synchronization, and signals & timers on the way.

### 1. Process Creation  
We're using Python’s `multiprocessing` module to handle the alien enemies each separate processes. This lets the main game run independently while the aliens are offloaded to child processes.

Here is an image to the code snippet within os_game_utils.py where processes are used:
<img width="831" alt="image" src="https://github.com/user-attachments/assets/2661724c-abbd-4456-bd90-f01b2743da62" />

### 2. Threading  
Threads help the game stay smooth by running several things at once—like reading player input, checking for collisions, and playing background music. That way, the game doesn’t freeze when doing something heavy.

Here is an image to the code snippet within os_game_utils.py where threads are used:
<img width="622" alt="image" src="https://github.com/user-attachments/assets/7de76f6c-fe65-4406-874c-b3e1c5569098" />


### 3. Inter-process Communication (IPC)  
We plan to use shared memory and message passing between the main game process and the alien wave processes. This will allow us to send commands like when to spawn new enemies, change direction, or increase speed. It will demonstrate how separate processes in an operating system can communicate without interfering with each other.

Work in Progress: We plan on further iterating upon our code until IPC is added. We wanted to focus on the core gameplay before we added IPC.

### 4. Synchronization  
We’re planning to implement synchronization tools like locks and semaphores to manage access to shared resources—such as power-ups and the high score file. The goal is to prevent race conditions when two parts of the game (like the player and an alien) try to access or modify the same resource at the same time.

Work in Progress: We plan on further iterating upon our code until synchronization is added. We wanted to focus on the core gameplay before we added synchronization.

### 5. Signals and Timers  
We intend to use signal handling and timers to manage bullet events—like automatically removing bullets after a certain time or when they go off-screen. This is similar to how operating systems use signals and timers to manage timed tasks and alert processes when events occur.

Work in Progress: We plan on further iterating upon our code until signals and timers are added. We wanted to focus on the core gameplay before we added signals and timers.

## What’s Next  
Here’s what we’re planning to add before the final version:
- Better scoring system, with visible score updates  
- Increasing alien speed as difficulty ramps up  
- Random power-ups to make things more exciting  
- Sound effects and visual feedback for hits and explosions  
- A high score system to track the best players  
