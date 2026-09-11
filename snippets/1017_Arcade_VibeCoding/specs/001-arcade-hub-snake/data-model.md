# Data Model: Arcade Hub Canvas RPG + Snake

**Date**: 2026-05-12  
**Feature**: Arcade Hub Canvas RPG + Snake  
**Purpose**: Define the scene state, entities, relationships, and validation rules for the top-down Hub rewrite.

## Core Entities

### 1. Hub Scene State

**Purpose**: Represents the active Canvas room and the objects inside it.

```typescript
interface HubSceneState {
  roomWidth: number;
  roomHeight: number;
  player: PlayerAvatarState;
  machines: ArcadeMachineState[];
  interactionPrompt: InteractionPromptState;
  transition: SceneTransitionState;
}
```

**Validation Rules**:
- `roomWidth` and `roomHeight` are positive integers.
- `player` is always present and remains inside room bounds after each movement update.
- `machines` contains at least one interactive machine in the MVP.
- `interactionPrompt.visible` reflects proximity to the active machine.
- `transition.targetScene` is only set when the player triggers a launch.

---

### 2. Player Avatar State

**Purpose**: Represents the player's position and movement inside the Hub room.

```typescript
interface PlayerAvatarState {
  x: number;
  y: number;
  width: number;
  height: number;
  speed: number;
  facing: "up" | "down" | "left" | "right";
  isMoving: boolean;
}
```

**Validation Rules**:
- `x` and `y` remain within the room after collision resolution.
- `width` and `height` are positive and small enough to fit inside the room.
- `speed` is a positive number.
- `facing` must be one of the four cardinal directions.

---

### 3. Arcade Machine State

**Purpose**: Represents the Snake cabinet and its interaction area.

```typescript
interface ArcadeMachineState {
  id: string;
  kind: "snake";
  x: number;
  y: number;
  width: number;
  height: number;
  interactionRadius: number;
  isInteractive: boolean;
}
```

**Validation Rules**:
- `id` is a non-empty unique string.
- `kind` is fixed to `snake` for the MVP.
- `interactionRadius` is positive and larger than the player collision box.
- `isInteractive` is true for the active machine in the MVP.

---

### 4. Interaction Prompt State

**Purpose**: Controls the `[E]` hint shown when the player is near a machine.

```typescript
interface InteractionPromptState {
  visible: boolean;
  text: string;
  machineId: string | null;
  screenX: number;
  screenY: number;
}
```

**Validation Rules**:
- `visible` is true only when the player is within interaction range.
- `text` is a short prompt such as `[E] Játék indítása`.
- `machineId` matches the nearby machine when visible, otherwise `null`.
- `screenX` and `screenY` are derived from room coordinates and canvas scaling.

---

### 5. Scene Transition State

**Purpose**: Represents switching from the Hub scene into Snake and back again.

```typescript
type SceneId = "hub" | "snake";

interface SceneTransitionState {
  currentScene: SceneId;
  targetScene: SceneId | null;
  requestedByMachineId: string | null;
  pending: boolean;
}
```

**Validation Rules**:
- `currentScene` is always one of the known scene IDs.
- `targetScene` is only set during a launch request.
- `requestedByMachineId` identifies the cabinet that triggered the transition.
- `pending` is true only while the app is switching scenes.

---

### 6. Proximity Result

**Purpose**: Captures the outcome of a player-to-machine range check.

```typescript
interface ProximityResult {
  machineId: string | null;
  inRange: boolean;
  distance: number;
}
```

**Validation Rules**:
- `distance` is zero or greater.
- `inRange` is true when `distance` is inside the machine's interaction radius.
- `machineId` is null when no machine is near enough to interact with.

---

## Preserved Existing Models

The following models remain unchanged from the existing implementation and are reused by the Canvas Hub pivot:

- `SnakeGameState`
- `HighScoreData`
- `InputQueue`
- `CollisionResult`

Those models continue to belong to the Snake module and storage layer, not the Hub rewrite.

## Relationships & State Flow

### Hub Flow

```text
HubSceneState
  ├── player -> PlayerAvatarState
  ├── machines[] -> ArcadeMachineState
  ├── interactionPrompt -> InteractionPromptState
  └── transition -> SceneTransitionState
```

### Interaction Flow

```text
Player movement
  -> ProximityResult
  -> InteractionPromptState.visible
  -> press E when in range
  -> SceneTransitionState.targetScene = "snake"
  -> Snake module loads
  -> return to Hub
```

### Rendering Flow

```text
HubSceneState
  -> drawHub()
  -> room background
  -> player rectangle
  -> machine rectangle
  -> interaction prompt overlay
```

## Notes

- The Hub uses placeholder rectangles only in the MVP.
- The Snake module remains an isolated scene with its own state and tests.
- The interaction boundary is intentionally small: the Hub only needs enough state to decide proximity and launch the existing Snake game.
