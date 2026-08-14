import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HomePage } from '../HomePage';

describe('HomePage', () => {
  it('closes Quick Log modal when Escape is pressed', () => {
    render(<HomePage />);

    // Open a quick log tile
    fireEvent.click(screen.getByText(/Flow/i));

    expect(screen.getByRole('dialog')).toBeInTheDocument();

    fireEvent.keyDown(window, { key: 'Escape' });

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
