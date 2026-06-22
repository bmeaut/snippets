/**
 * Room Navigation Contract
 *
 * Describes the minimal room transition state shared by the Hub and Casino
 * scenes so door interactions can be implemented consistently.
 */

export type SceneId = 'hub' | 'casino';

export interface RoomTransitionState {
  currentScene: SceneId;
  targetScene: SceneId | null;
  interactionTargetId: string | null;
  pending: boolean;
}

export interface RoomExitDefinition {
  id: string;
  targetScene: SceneId;
  side: 'left' | 'right';
  prompt: string;
}

export const validateRoomTransitionState = (state: any): state is RoomTransitionState => {
  return (
    state &&
    (state.currentScene === 'hub' || state.currentScene === 'casino') &&
    (state.targetScene === null || state.targetScene === 'hub' || state.targetScene === 'casino') &&
    (state.interactionTargetId === null || typeof state.interactionTargetId === 'string') &&
    typeof state.pending === 'boolean'
  );
};