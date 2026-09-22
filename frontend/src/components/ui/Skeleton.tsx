import React from "react";
import { cn } from "@/lib/utils";

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn("animate-pulse bg-slate-800/80 rounded-md", className)}
    {...props}
  />
);
