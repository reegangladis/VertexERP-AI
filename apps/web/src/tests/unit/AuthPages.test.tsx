import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { NotificationProvider } from '@/store/NotificationContext';
import { Login, Register } from '@/pages/AuthPages';
import { expect, test } from 'vitest';

test('renders login form items', () => {
  render(
    <NotificationProvider>
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    </NotificationProvider>
  );

  expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
});

test('renders register form items', () => {
  render(
    <NotificationProvider>
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    </NotificationProvider>
  );

  expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument();
});
