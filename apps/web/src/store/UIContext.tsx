import React, { createContext, useContext, useState } from 'react';

interface UIContextType {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  activeModalId: string | null;
  openModal: (id: string) => void;
  closeModal: () => void;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

export function UIProvider({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setSidebarOpenState] = useState(true);
  const [activeModalId, setActiveModalId] = useState<string | null>(null);

  const toggleSidebar = () => setSidebarOpenState((prev) => !prev);
  const setSidebarOpen = (open: boolean) => setSidebarOpenState(open);
  const openModal = (id: string) => setActiveModalId(id);
  const closeModal = () => setActiveModalId(null);

  return (
    <UIContext.Provider
      value={{
        isSidebarOpen,
        toggleSidebar,
        setSidebarOpen,
        activeModalId,
        openModal,
        closeModal,
      }}
    >
      {children}
    </UIContext.Provider>
  );
}

export function useUI() {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
}
