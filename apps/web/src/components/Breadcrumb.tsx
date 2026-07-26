import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1.5 md:space-x-2 text-xs font-medium text-muted-foreground select-none">
        <li className="inline-flex items-center">
          <Link
            to="/"
            className="inline-flex items-center hover:text-foreground transition-colors duration-150"
          >
            <Home className="mr-2 h-3.5 w-3.5" />
            Home
          </Link>
        </li>
        {items.map((item, index) => (
          <li key={index} className="inline-flex items-center">
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50 mx-1 md:mx-2" />
            {item.path ? (
              <Link
                to={item.path}
                className="hover:text-foreground transition-colors duration-150"
              >
                {item.label}
              </Link>
            ) : (
              <span className="text-foreground font-semibold">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
export default Breadcrumb;
