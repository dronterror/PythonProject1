import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Custom render function that includes providers
export function renderWithProviders(ui, options = {}) {
  const AllTheProviders = ({ children }) => {
    return (
      <BrowserRouter>
        {children}
      </BrowserRouter>
    )
  }

  return render(ui, { wrapper: AllTheProviders, ...options })
}

// Mock API responses
export const mockApiResponses = {
  drugs: [
    {
      id: 1,
      name: "Aspirin",
      form: "Tablet",
      strength: "500mg",
      current_stock: 100,
      low_stock_threshold: 10
    },
    {
      id: 2,
      name: "Ibuprofen",
      form: "Capsule",
      strength: "400mg",
      current_stock: 50,
      low_stock_threshold: 15
    }
  ],
  orders: [
    {
      id: 1,
      patient_name: "John Doe",
      drug_id: 1,
      dosage: 2,
      schedule: "Every 8 hours",
      status: "active",
      doctor_id: 1,
      created_at: "2025-06-21T10:00:00Z"
    }
  ],
  administrations: [
    {
      id: 1,
      order_id: 1,
      nurse_id: 2,
      administration_time: "2025-06-21T10:30:00Z"
    }
  ]
}

// Mock user data
export const mockUsers = {
  doctor: {
    id: 1,
    email: "doctor@test.com",
    role: "doctor",
    api_key: "doctor_api_key"
  },
  nurse: {
    id: 2,
    email: "nurse@test.com",
    role: "nurse",
    api_key: "nurse_api_key"
  },
  pharmacist: {
    id: 3,
    email: "pharmacist@test.com",
    role: "pharmacist",
    api_key: "pharmacist_api_key"
  }
}

// Helper to mock localStorage
export const mockLocalStorage = (data = {}) => {
  const mock = {
    getItem: vi.fn((key) => data[key] || null),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  Object.defineProperty(window, 'localStorage', {
    value: mock,
    writable: true,
  })
  return mock
}

// Helper to mock sessionStorage
export const mockSessionStorage = (data = {}) => {
  const mock = {
    getItem: vi.fn((key) => data[key] || null),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  Object.defineProperty(window, 'sessionStorage', {
    value: mock,
    writable: true,
  })
  return mock
}

// Helper to wait for async operations
export const waitFor = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms))

// Helper to mock fetch
export const mockFetch = (response, status = 200) => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(response),
    text: () => Promise.resolve(JSON.stringify(response)),
  })
}

// Helper to mock axios
export const mockAxios = (response, status = 200) => {
  const axios = require('axios')
  axios.get = vi.fn().mockResolvedValue({ data: response, status })
  axios.post = vi.fn().mockResolvedValue({ data: response, status })
  axios.put = vi.fn().mockResolvedValue({ data: response, status })
  axios.delete = vi.fn().mockResolvedValue({ data: response, status })
} 