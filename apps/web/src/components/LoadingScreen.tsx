import { Loader2 } from 'lucide-react';

export function LoadingScreen() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-foreground" />
        <p className="text-sm font-medium tracking-wider text-muted-foreground uppercase">
          Initializing Enterprise Environment...
        </p>
      </div>
    </div>
  );
}
export default LoadingScreen;
