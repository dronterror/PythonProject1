import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Make vi globally available
global.vi = vi

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.sessionStorage = sessionStorageMock

// Mock navigator
Object.defineProperty(window, 'navigator', {
  value: {
    userAgent: 'node.js',
    serviceWorker: {
      register: vi.fn(),
    },
  },
  writable: true,
})

// Mock PWA registration
global.registration = {
  showNotification: vi.fn(),
  pushManager: {
    subscribe: vi.fn(),
    getSubscription: vi.fn(),
  },
}

// Mock Keycloak instead of Auth0
global.fetch = vi.fn()

// Mock environment variables
process.env.NODE_ENV = 'test'

// Extend expect with jest-dom matchers
import { expect } from 'vitest'
import * as matchers from '@testing-library/jest-dom/matchers'
expect.extend(matchers) 