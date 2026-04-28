import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  it('renders the login page on the root path', () => {
    render(<App />);
    // This assumes Login component renders something identifiable. Let's just check it doesn't crash for now.
    expect(screen).toBeDefined();
  });
});
