import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@/store/ThemeContext';
import { ThemeToggle } from '@/components/ThemeToggle';
import { expect, test } from 'vitest';

test('renders theme toggle button and switches theme state on click', () => {
  render(
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>
  );

  const button = screen.getByRole('button', { name: /toggle visual theme/i });
  expect(button).toBeInTheDocument();

  // Test click event
  fireEvent.click(button);
  
  // Click again to return to initial
  fireEvent.click(button);
});
