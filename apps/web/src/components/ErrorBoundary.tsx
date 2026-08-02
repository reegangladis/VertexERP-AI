import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ErrorLayout } from '@/layouts/ErrorLayout';
import { Button } from './Button';
import { AlertOctagon } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error inside ErrorBoundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorLayout>
          <div className="flex justify-center text-destructive mb-2">
            <AlertOctagon className="h-12 w-12" />
          </div>
          <h2 className="text-xl font-bold text-foreground">Application Render Failed</h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            An unexpected error occurred while rendering the page view.
          </p>
          {this.state.error && (
            <code className="block text-xs font-mono bg-background border border-border px-3 py-2 rounded text-destructive overflow-auto max-h-40 select-all">
              {this.state.error.message}
            </code>
          )}
          <div className="pt-4">
            <Button variant="outline" onClick={this.handleReset} className="w-full">
              Reset Application state
            </Button>
          </div>
        </ErrorLayout>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
