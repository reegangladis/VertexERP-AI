import React from "react";
import { Link, useLocation } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  to?: string;
}

export interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  homePath?: string;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, homePath = "/" }) => {
  const location = useLocation();

  const generatedItems = React.useMemo(() => {
    if (items) return items;
    const paths = location.pathname.split("/").filter(Boolean);
    return paths.map((segment, index) => {
      const url = `/${paths.slice(0, index + 1).join("/")}`;
      const label = segment
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
      return { label, to: index < paths.length - 1 ? url : undefined };
    });
  }, [items, location.pathname]);

  if (generatedItems.length === 0) return null;

  return (
    <nav className="flex items-center space-x-1.5 text-xs text-slate-400 mb-4" aria-label="Breadcrumb">
      <Link
        to={homePath}
        className="flex items-center text-slate-400 hover:text-slate-200 transition-colors"
      >
        <Home className="w-3.5 h-3.5" />
      </Link>

      {generatedItems.map((item, index) => {
        const isLast = index === generatedItems.length - 1;
        return (
          <React.Fragment key={index}>
            <ChevronRight className="w-3 h-3 text-slate-600 shrink-0" />
            {item.to && !isLast ? (
              <Link
                to={item.to}
                className="hover:text-slate-200 transition-colors font-medium text-slate-400 truncate max-w-[150px]"
              >
                {item.label}
              </Link>
            ) : (
              <span className="font-semibold text-slate-200 truncate max-w-[200px]">
                {item.label}
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
