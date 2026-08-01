import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// React Testing Library mounts into a container appended to document.body.
// Without an explicit unmount, a component from a previous test stays in
// the DOM and `getByRole` starts matching two elements — which surfaces as
// a confusing "found multiple elements" failure in an unrelated test.
afterEach(() => {
  cleanup();
});

// jsdom implements neither of these, and both are used by code under test
// (charts measure layout, pages scroll to top on navigation). Stubbing them
// here rather than in each test keeps the failures that matter visible.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

window.scrollTo = vi.fn();

if (!window.ResizeObserver) {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
}
