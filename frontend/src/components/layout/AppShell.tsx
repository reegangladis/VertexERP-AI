import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export const AppShell: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-[#070b14] text-slate-100 antialiased selection:bg-indigo-500 selection:text-white relative overflow-hidden">
      {/* Ambient Radial Background Glows */}
      <div className="pointer-events-none fixed -top-32 left-1/3 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-indigo-600/5 blur-[150px]" />
      <div className="pointer-events-none fixed -bottom-32 right-[-5%] h-[400px] w-[600px] rounded-full bg-purple-600/5 blur-[140px]" />

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
