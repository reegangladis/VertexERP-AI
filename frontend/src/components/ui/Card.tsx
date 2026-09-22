import React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
}


export const Card: React.FC<CardProps> = ({
  className,
  title,
  subtitle,
  children,
  ...props
}) => (
  <div
    className={cn(
      "bg-slate-900/60 border border-slate-800 rounded-xl shadow-lg backdrop-blur-sm",
      className
    )}
    {...props}
  >
    {(title || subtitle) && (
      <div className="px-6 py-5 border-b border-slate-800/80">
        {title && <h3 className="text-base font-semibold text-slate-100">{title}</h3>}
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
    )}
    {children}
  </div>
);


export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn("px-6 py-5 border-b border-slate-800/80 flex items-center justify-between", className)} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className,
  children,
  ...props
}) => (
  <h3 className={cn("text-base font-semibold text-slate-100", className)} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className,
  children,
  ...props
}) => (
  <p className={cn("text-xs text-slate-400 mt-0.5", className)} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn("p-6", className)} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn("px-6 py-4 border-t border-slate-800/80 bg-slate-900/40 rounded-b-xl flex items-center justify-end gap-3", className)} {...props}>
    {children}
  </div>
);
