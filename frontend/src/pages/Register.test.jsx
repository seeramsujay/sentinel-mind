import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Register from './Register';

describe('Register Component', () => {
  it('renders the registration form', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
    
    expect(screen.getAllByText(/SENTINELMIND/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Full Name/i)).toBeDefined();
    expect(screen.getByText(/Work Email/i)).toBeDefined();
    expect(screen.getByText(/Operational Role/i)).toBeDefined();
    expect(screen.getByPlaceholderText(/Commander Name/i)).toBeDefined();
    expect(screen.getByText(/REQUEST ACCESS/i)).toBeDefined();
  });
});
