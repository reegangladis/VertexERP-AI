import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { NotFound } from '@/routes/NotFound';
import { expect, test } from 'vitest';

test('renders 404 page with titles and navigation actions', () => {
  render(
    <BrowserRouter>
      <NotFound />
    </BrowserRouter>
  );

  expect(screen.getByText('404')).toBeInTheDocument();
  expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /back to overview/i })).toBeInTheDocument();
});
