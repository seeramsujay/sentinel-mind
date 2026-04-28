import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

describe('Header Component', () => {
  it('renders the navigation links and brand', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/SENTINELMIND/i)).toBeDefined();
    expect(screen.getByText(/Dashboard/i)).toBeDefined();
    expect(screen.getByText(/Asset Tree/i)).toBeDefined();
    expect(screen.getByText(/Field Upload/i)).toBeDefined();
    expect(screen.getByText(/OPERATIONAL/i)).toBeDefined();
  });
});
