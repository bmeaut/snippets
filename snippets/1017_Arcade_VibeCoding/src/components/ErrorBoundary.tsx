import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  onReturnToMenu: () => void;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false };

  public static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Game module crashed', error, info);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <main className="error-state">
          <h2>Game failed to load.</h2>
          <p>The hub is still available. Return to the hub and try again.</p>
          <button className="primary-button" onClick={this.props.onReturnToMenu}>
            Return to hub
          </button>
        </main>
      );
    }

    return this.props.children;
  }
}
