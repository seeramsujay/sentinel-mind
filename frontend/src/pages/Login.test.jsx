import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from './Login';

describe('Login Component', () => {
  it('renders the login form', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    // Check for SENTINELMIND branding
    expect(screen.getAllByText(/SENTINELMIND/i).length).toBeGreaterThan(0);
    
    // Check for specific labels using more flexible queries or placeholders
    expect(screen.getByPlaceholderText(/name@organization\.com/i)).toBeDefined();
    expect(screen.getByPlaceholderText(/••••••••••••/i)).toBeDefined();
    expect(screen.getByText(/ACCESS COMMAND CENTER/i)).toBeDefined();
  });
});
