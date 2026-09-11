import type { InteractionPromptState } from '../systems/interaction';

interface InteractionPromptProps {
  prompt: InteractionPromptState;
}

export function InteractionPrompt({ prompt }: InteractionPromptProps) {
  if (!prompt.visible) {
    return null;
  }

  return (
    <div
      className="hub-prompt"
      style={{
        left: `${prompt.screenX}px`,
        top: `${prompt.screenY}px`,
      }}
    >
      {prompt.text}
    </div>
  );
}