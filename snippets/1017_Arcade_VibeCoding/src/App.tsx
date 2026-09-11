import { useState } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { HubScene } from './hub/scene/HubScene';
import { SnakeGame } from './games/snake/SnakeGame';
import { AmoebaGame } from './games/ameoba/AmoebaGame';
import CasinoScene from './casino/scene/CasinoScene';
import { BlackjackGame } from './games/blackjack/BlackjackGame';
import { RouletteGame } from './games/roulette/RouletteGame';
import type { RoomSpawnSide } from './hub/entities/player';

type SceneId = 'hub' | 'snake' | 'amoba' | 'casino' | 'blackjack' | 'roulette';
export default function App() {
  const [scene, setScene] = useState<SceneId>('hub');
  const [hubSpawnSide, setHubSpawnSide] = useState<RoomSpawnSide>('left');
  const [casinoSpawnSide, setCasinoSpawnSide] = useState<RoomSpawnSide>('left');

  let content: JSX.Element;

  if (scene === 'hub') {
    content = (
      <HubScene
        spawnSide={hubSpawnSide}
        onLaunchSnake={() => setScene('snake')}
        onLaunchAmeoba={() => setScene('amoba')}
        onLaunchCasino={() => {
          setCasinoSpawnSide('left');
          setScene('casino');
        }}
      />
    );
  } else if (scene === 'snake') {
    content = (
      <ErrorBoundary onReturnToMenu={() => setScene('hub')}>
        <SnakeGame onReturnToMenu={() => { setHubSpawnSide('left'); setScene('hub'); }} />
      </ErrorBoundary>
    );
  } else if (scene === 'amoba') {
    content = (
      <ErrorBoundary onReturnToMenu={() => setScene('hub')}>
        <AmoebaGame onReturnToMenu={() => { setHubSpawnSide('left'); setScene('hub'); }} />
      </ErrorBoundary>
    );
  } else if (scene === 'casino') {
    content = (
      <ErrorBoundary onReturnToMenu={() => setScene('hub')}>
        <CasinoScene
          spawnSide={casinoSpawnSide}
          onReturnToHub={() => {
            setHubSpawnSide('right');
            setScene('hub');
          }}
          onLaunchRoulette={() => setScene('roulette')}
          onLaunchBlackjack={() => setScene('blackjack')}
        />
      </ErrorBoundary>
    );
  } else if (scene === 'blackjack') {
    content = (
      <ErrorBoundary onReturnToMenu={() => setScene('casino')}>
        <BlackjackGame onReturnToMenu={() => setScene('casino')} />
      </ErrorBoundary>
    );
  } else {
    content = (
      <ErrorBoundary onReturnToMenu={() => setScene('casino')}>
        <RouletteGame onReturnToMenu={() => setScene('casino')} />
      </ErrorBoundary>
    );
  }

  return content;
}
