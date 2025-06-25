import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@mui/material/styles'
import { theme } from '@/theme'

// Mock users for testing
export const mockUsers = {
  doctor: {
    id: 'doctor-123',
    name: 'Dr. Test Doctor',
    email: 'doctor@test.com',
    role: 'doctor',
    sub: 'auth0|doctor123',
    picture: 'https://example.com/doctor.jpg'
  },
  nurse: {
    id: 'nurse-123',
    name: 'Test Nurse',
    email: 'nurse@test.com',
    role: 'nurse',
    sub: 'auth0|nurse123',
    picture: 'https://example.com/nurse.jpg'
  },
  pharmacist: {
    id: 'pharmacist-123',
    name: 'Test Pharmacist',
    email: 'pharmacist@test.com',
    role: 'pharmacist',
    sub: 'auth0|pharmacist123',
    picture: 'https://example.com/pharmacist.jpg'
  }
}

// Mock API responses
export const mockApiResponses = {
  orders: [
    {
      id: 'order-1',
      patientName: 'John Doe',
      drugName: 'Aspirin',
      dosage: 500,
      status: 'active',
      createdAt: '2024-01-01T00:00:00Z',
      schedule: 'Every 8 hours'
    }
  ],
  drugs: [
    {
      id: 'drug-1',
      name: 'Aspirin',
      strength: '500mg',
      dosage_form: 'Tablet',
      quantity: 100,
      reorder_level: 10
    }
  ],
  patients: [
    {
      id: 'patient-1',
      name: 'John Doe',
      bed_number: '101',
      overdue_count: 0,
      due_count: 2
    }
  ]
}

// Custom render function with all providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[]
}

export function renderWithProviders(
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
) {
  const { initialEntries = ['/'], ...renderOptions } = options
  
  // Create a new QueryClient for each test
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      React.createElement(
        ThemeProvider,
        { theme },
        React.createElement(
          BrowserRouter,
          {},
          children
        )
      )
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Re-export everything from testing-library
export * from '@testing-library/react' 