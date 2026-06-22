# GAME SPECIFICATION: Python/Pygame Bomberman Clone

## 1. Game Overview
- **Core Loop**: Navigate a grid-based maze, place bombs to destroy obstacles, defeat wandering enemies, and find the hidden exit to progress.
- **Genre**: 2D Arcade / Action-Puzzle
- **Engine/Stack**: Python 3.x, **Pygame** (or `pygame-ce`) using a `venv` (virtual environment)

## 2. Core Game Mechanics
### The World
- **Grid Layout**: The playing field is a grid (e.g., 15x13 tiles).
- **Indestructible Walls**: Placed along the outer boundaries and in a fixed checkered pattern on the inside. Protects against explosions.
- **Destructible Blocks**: Scattered randomly in the empty grid spaces. Can be destroyed by bomb explosions. Upon destruction, they may reveal a Power-Up or the Level Exit Door.

### Characters (Humans & Bots)
- **Unified Entity**: Both human players and AI bots share the exact same physical capabilities, unified under a standard "Character." 
- **Movement**: 4-directional (Up, Down, Left, Right). Moves strictly along the grid.
- **Bomb Placement**: Drops a bomb on the current grid tile. Each character can only drop a fixed amount of bombs at once (initially 1).
- **Vulnerability**: Dies instantly if caught in a bomb blast or (in Story Mode) if touched by a wandering monster.
- **Controllers**: A human player pilots the character using Keyboard/Gamepad inputs. An AI pilot dynamically analyzes the grid to pilot the character (navigating to targets, dodging bombs).

### Bombs & Explosions
- **Ownership**: Bombs track which Character ID placed them to properly award kills and points.
- **Timer**: Bombs detonate automatically after a fuse timer (e.g., 2.5 seconds).
- **Area of Effect**: Detonation creates a cross-shaped explosion (Up, Down, Left, Right). The blast stops at indestructible walls but penetrates and destroys destructible blocks.
- **Chain Reactions**: An explosion hitting an unexploded bomb causes it to detonate instantly.

### Story Mode Monsters
- **Basic Monster**: Wanders the corridors automatically. Changes direction when hitting a wall or block. Exists only in Story Mode to serve as basic hazards.
- **Defeat**: Killed instantly if caught in a bomb explosion.

### Power-Ups (Hidden in blocks)
- **Bomb Up**: Increases the maximum number of simultaneous bombs the character can place.
- **Fire Up**: Increases the explosion range by 1 tile in all 4 directions for that character.
- **Speed Up**: Increases character movement speed.

## 3. Menu System & Game States
A **State Machine** architecture will manage the flow of the application.
1. **Main Menu**: Title graphic and selectable text options ("Start Story Mode", "Start Multiplayer Mode", "Quit").
2. **Story Mode State**: The standard Single-Player Bomberman experience (finding the exit, defeating enemies).
3. **Multiplayer League/Tournament State**: A separate mode pitting 4 characters (Human or AI) against each other without standard wandering enemies or an exit door.
4. **Pause Menu**: Triggered by hitting `ESC` during gameplay. Pauses action; shows "Resume" and "Quit to Menu".
5. **Level Transition/Round Over**: 
    - *Story Mode*: Shows "Level Cleared - Going to Level X".
    - *Multiplayer Mode*: Displays the scoreboard showing wins/kills between rounds.
6. **Game Over**: Triggered when the player loses lives (Story Mode) or when the tournament ends (Multiplayer Mode goal reached).

## 4. Technical Architecture
Using Object-Oriented Programming (OOP) to handle game entities.

### Project Structure (File Separation):
To keep the codebase maintainable, avoid bloated single scripts. Separate classes into distinct modules:
- `main.py`: The entry point. Initializes Pygame and instantiates the state loop.
- `states.py` / `state_manager.py`: Contains the `StateManager` and individual classes for menus/game modes.
- `session.py`: Contains the `SessionManager` to track multiplayer scores and settings.
- `entities/character.py`: The `Character` sprite class and base parameters.
- `entities/bomb.py`: The `Bomb` and `Explosion` sprite logic.
- `entities/block.py`: Indestructible walls, destructible blocks, and power-ups.
- `entities/monster.py`: Standard Story Mode wandering enemies.
- `controllers/input_controller.py`: Keyboard mappings for WASD/Arrow Keys.
- `controllers/ai_controller.py`: Bot navigation and logic.
- `level/map_manager.py`: Grid layout generation and parsing.
- `utils/constants.py`: Global constants (Tile size, screen width, colors, FPS limit).

### Core Classes:
- **`Sprite` classes (inheriting from `pygame.sprite.Sprite`)**:
  - `Character`: Unifies the concept of "Players" and "Enemies". Handles grid-aligned movement, animation state, bomb placement physics, and collision logic. (Replaces `Player` and `Enemy` logic to support Multiplayer seamlessly).
  - `Bomb`: Handles the ticking fuse and spawning `Explosion` objects. Retains the ID of the `Character` who placed it.
  - `Explosion`: Disappears after a fraction of a second; handles collision checks against blocks, characters, and other bombs.
  - `Block`: Represents both destructible and indestructible grid spaces.
  - `PowerUp`: Waits for a character to collide with it to apply a buff.
- **Controller Classes (Dependency Injection for `Character`)**:
  - `InputController`: Maps keyboard/gamepad events (WASD, Arrows) to movement and bomb-drop commands. 
  - `AIController`: Analyzes the grid logic and sends movement/bomb commands to simulate a bot.
- **Managers**:
  - `MapManager`: Generates a 2D array representing the board. Spawns walls, destructible blocks, player start positions, and handles the map grid state.
  - `SessionManager`: Manages the overall series of matches (Tournament/Story). Tracks active mode, player scores, tiered points (1st/2nd/3rd place), remaining lives, the scoring goal, and handles swapping between rounds.
  - `StateManager`: Controls switching between the active rendering/event loops (Menu, Multiplayer Setup, Story Match, Multiplayer Match, Scoreboard, Game Over).

### Scalability & Future-Proofing Requirements:
To ensure the game can seamlessly transition to multiplayer and tournament features later on, adhere to the following architectural patterns from the start:
- **Character Controller Interface**: To seamlessly allow 4 characters on the map (a mix of human and AI players), abstract the control mechanism out of the core `Character` class. A `Character` should receive movement and bomb commands. An `InputController` will provide commands from keyboard (Human), while an `AIController` will generate commands based on logic (Bot).
- **Player Identification**: Add an `ID` or `PlayerNumber` attribute to the `Character` class right away. Tie bombs, scores, and statistics to this ID to easily track who kills whom, who wins the round, and overall series scoring.
- **Data-Driven Level Settings**: The `MapManager` should accept configuration parameters (e.g., `grid_size`, `num_destructible_blocks`, `enemy_spawn_rate`, `player_start_positions`). This prevents hardcoding the map layout and makes "Tournament Mode" special modifiers (like smaller arenas or no enemies) trivial to implement later.
- **Session/Round Management layer**: Ensure there is a distinct separation between an active "Match" (gameplay) and a "Session" (the overall series of matches). Scores, tiered placements, and the configurable end-goals should be entirely managed by the `SessionManager`, leaving the physical `Map` isolated.

### Unit Testing Requirements:
To ensure the game logic is robust and independent of the rendering cycle, decouple core logic from Pygame specifics (such as screen rendering) wherever possible. Recommended test coverage (using `unittest` or `pytest`):

**Core/Story Mode Tests:**
- **Map Generation**: Test that the `MapManager` correctly generates a 15x13 grid with indestructible walls in the exact checkered pattern and places the correct number of destructible blocks.
- **Player Movement Validation**: Test that the player cannot move into wall/block tiles and correctly updates grid coordinates.
- **Bomb Placement and Explosions**: Validate that bomb limits are respected (player cannot place more bombs than their allowed max). Test explosion area of effect logic, ensuring it stops at indestructible walls but correctly triggers block destruction.
- **State Management**: Verify that state transitions trigger correctly (e.g., losing a life transitions to Game Over when lives equal 0).
- **Power-Up Logic**: Test that collecting a power-up updates the correct player attributes (speed, bomb limit, or fire range).

**Multiplayer/Tournament Mode Tests:**
- **Mode Isolation**: Verify that when "Multiplayer Mode" is initialized, standard single-player features (hidden exit door, normal wandering enemies) do NOT spawn.
- **Multi-Character Spawning**: Assert that exactly 4 character entities are generated and placed in the outermost corner coordinates of the map matrix.
- **Match Conclusion & Tiered Scoring**: Validate that when a multiplayer match ends, the `SessionManager` correctly awards 3 points to the last survivor, 2 points to the runner-up, etc.
- **Tournament Goal Logic**: Test that the game loop accurately restarts the grid if the Goal Points have not been met, but properly triggers the Final Champion Screen when a player's score crosses the goal.
- **Tournament Modifiers**: Ensure that applying special configuration modifiers (e.g., maximum fire power on spawn) correctly overrides default character and map states during tests.

## 5. Implementation Milestones (Prompts for Future AI Dialogues)
*When you start building, you can feed this spec to the AI and ask it to complete these phases one by one:*

- **Milestone 1 (Setup)**: "Set up the Pygame boilerplate, the main application loop, state manager, and a basic interactive Main Menu."
- **Milestone 2 (The Grid)**: "Implement the Level Manager. Generate a static 15x13 grid with indestructible walls in a checkered pattern and place random destructible blocks."
- **Milestone 3 (The Character)**: "Create the unified Character sprite class with a generic Controller interface. Implement 4-directional movement with collision detection against the walls and blocks using a basic Keyboard Input Controller."
- **Milestone 4 (Bombs & Explosions)**: "Add the ability for the Character to place bombs on the grid tied to their specific Player ID. Implement a 3-second fuse, the cross-shaped blast radius, and logic to destroy destructible blocks without passing through indestructible walls."
- **Milestone 5 (Story Mode Monsters)**: "Add a basic Monster class strictly for Story Mode. Implement logic so the monster automatically wanders the grid, bounces off walls, and kills the player on touch. Ensure the monster can be killed by explosions."
- **Milestone 6 (Core Gameplay Loop)**: "Add the hidden Level Exit Door (spawns under a random block) and Power-Ups. Tie the Win/Lose conditions to the State Manager."
- **Milestone 7 (Polish)**: "Add sprite images/animations, sound effects, UI (score/lives/bombs available), and a pause menu."
- **Milestone 8 (Local Multiplayer Branching)**: "Expand the Main Menu to include a dedicated 'Start Multiplayer Mode' option. Before entering the gameplay state, prompt the user with a setup screen to select the number of Human Players (1 or 2) and set a 'Goal Points to Reach' (e.g., 5, 10). Create a separate Gameplay State for this mode that disables the hidden exit door and wandering enemies. Spawn 4 characters (one in each corner), assigning InputControllers or AIControllers based on the setup screen."
- **Milestone 9 (Multiplayer Inputs & Combat)**: "Refactor character input to support Human and AI controllers. Allow mapping WASD to Character 1 and Arrow Keys to Character 2. Allow bombs to damage and kill other characters in Multiplayer Mode. Ensure that remaining AI characters default to basic idle/wandering logic."
- **Milestone 10 (Tournament League Scoring & Modifiers)**: "Create a 'Round Over' scoreboard screen for Multiplayer Mode. Apply points based on survival placement (1st place = 3 points, 2nd = 2 points, 3rd = 1 point, 4th = 0). Check against the 'Goal Points to Reach'; if no character has reached the goal, reset the grid for the next round. Optionally add modifiers per round (e.g., 'Sudden Death', 'Max Speed') and declare an overall champion when the goal is met."
- **Milestone 11 (Advanced AI Bots)**: "Upgrade the AIController for non-human characters. Allow them to smartly navigate away from bomb blasts, target destructible walls to gather power-ups, and aggressively try to trap human players and other bots."