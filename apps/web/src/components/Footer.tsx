import React from 'react';
import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="border-t border-border bg-secondary/10 w-full py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground gap-4 select-none">
        <p>© {new Date().getFullYear()} VertexERP AI. Enterprise Operating System.</p>
        <div className="flex space-x-6">
          <Link to="/" className="hover:underline transition-all">
            Overview
          </Link>
          <Link to="/dashboard" className="hover:underline transition-all">
            Dashboard
          </Link>
          <a href="/docs/Architecture.md" className="hover:underline transition-all">
            Docs
          </a>
          <span className="text-border">|</span>
          <span className="font-mono">Sprint 1.3 Foundation Completion</span>
        </div>
      </div>
    </footer>
  );
}
export default Footer;
