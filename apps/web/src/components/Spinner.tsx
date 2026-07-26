import React from 'react';

interface SpinnerProps extends React.HTMLAttributes<HTMLSpanElement> {
  size?: 'sm' | 'md' | 'lg';
}

export function Spinner({ size = 'md', className = '', ...props }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  };

  return (
    <span
      className={`inline-block rounded-full border-t-transparent border-current animate-spin ${sizes[size]} ${className}`}
      role="status"
      aria-label="loading"
      {...props}
    />
  );
}
export default Spinner;
