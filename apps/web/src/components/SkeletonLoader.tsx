import React from 'react';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'rect' | 'circle';
}

export function SkeletonLoader({
  variant = 'rect',
  className = '',
  ...props
}: SkeletonProps) {
  const variants = {
    text: 'h-4 w-full rounded',
    rect: 'h-24 w-full rounded-md',
    circle: 'h-12 w-12 rounded-full',
  };

  return (
    <div
      className={`animate-pulse bg-muted/60 ${variants[variant]} ${className}`}
      {...props}
    />
  );
}

export function TableSkeleton() {
  return (
    <div className="space-y-3 w-full">
      <SkeletonLoader variant="text" className="h-8 w-full" />
      <SkeletonLoader variant="rect" className="h-12 w-full" />
      <SkeletonLoader variant="rect" className="h-12 w-full" />
      <SkeletonLoader variant="rect" className="h-12 w-full" />
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="border border-border p-6 rounded-lg bg-card space-y-4">
      <SkeletonLoader variant="circle" />
      <SkeletonLoader variant="text" className="h-6 w-1/3" />
      <SkeletonLoader variant="text" className="h-4 w-2/3" />
      <SkeletonLoader variant="rect" className="h-20" />
    </div>
  );
}
export default SkeletonLoader;
