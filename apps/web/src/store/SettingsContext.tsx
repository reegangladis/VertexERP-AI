import React, { createContext, useContext, useState } from 'react';

interface FeatureFlags {
  enableBetaDashboard: boolean;
  enableTelemetry: boolean;
}

interface SettingsContextType {
  apiUrl: string;
  appVersion: string;
  featureFlags: FeatureFlags;
  toggleFeature: (flag: keyof FeatureFlags) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  // Read VITE_API_URL if present, otherwise default to local mock/development backend
  const [apiUrl] = useState(() => {
    return (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';
  });

  const [appVersion] = useState('1.3.0');

  const [featureFlags, setFeatureFlags] = useState<FeatureFlags>({
    enableBetaDashboard: false,
    enableTelemetry: true,
  });

  const toggleFeature = (flag: keyof FeatureFlags) => {
    setFeatureFlags((prev) => ({
      ...prev,
      [flag]: !prev[flag],
    }));
  };

  return (
    <SettingsContext.Provider
      value={{
        apiUrl,
        appVersion,
        featureFlags,
        toggleFeature,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}
