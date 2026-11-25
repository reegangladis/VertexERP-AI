import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAccentTheme } from "@/lib/theme";

export const AppShell: React.FC = () => {
  // Ensure user's selected zero-blue theme accent initializes on mount
  useAccentTheme();

  return (
    <div className="flex min-h-screen bg-[#09090b] bg-obsidian-grid text-zinc-100 antialiased selection:bg-brand-500 selection:text-white relative overflow-hidden">
      {/* Warm Carbon Ambient Radial Glows (Zero Blue) */}
      <div className="pointer-events-none fixed -top-32 left-1/3 h-[520px] w-[720px] -translate-x-1/2 rounded-full bg-brand-600/10 blur-[160px]" />
      <div className="pointer-events-none fixed -bottom-32 right-[-5%] h-[420px] w-[620px] rounded-full bg-amber-600/10 blur-[150px]" />

      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 relative z-10">
        <Header />
        <main className="flex-1 p-6 sm:p-8 overflow-y-auto custom-scrollbar">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
