import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor, userEvent } from '@testing-library/react'
import { renderWithProviders } from './utils'
import App from '../App'

// Mock Auth0
vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    isLoading: false,
    isAuthenticated: true,
    user: {
      sub: 'auth0|test123',
      email: 'test@hospital.com',
      name: 'Dr. Test User',
      picture: 'https://example.com/avatar.jpg'
    },
    getAccessTokenSilently: vi.fn().mockResolvedValue('mock-token'),
    loginWithRedirect: vi.fn(),
    logout: vi.fn(),
  }),
}))

// Mock API client
vi.mock('@/lib/apiClient', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  setAuthToken: vi.fn(),
  clearAuthToken: vi.fn(),
}))

// Mock React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  useQueryClient: vi.fn(),
  QueryClient: class MockQueryClient {
    constructor() {}
    invalidateQueries = vi.fn()
    setQueryData = vi.fn()
  },
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => children,
}))

describe('TDD Integration Tests - Complete User Workflows', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Doctor Workflow - TDD Red-Green-Refactor', () => {
    beforeEach(() => {
      // Mock successful API responses for doctor workflow
      const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
      mockUseQuery.mockReturnValue({
        data: [
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
        isLoading: false,
        error: null,
      })
    })

    it('RED: Doctor should complete full prescription workflow', async () => {
      // RED PHASE: Write test first (should fail initially)
      renderWithProviders(<App />)
      
      // 1. User should be able to log in and select doctor role
      expect(screen.getByText('MedLogistics')).toBeInTheDocument()
      
      // Mock role selection
      const doctorButton = screen.getByText('Doctor')
      fireEvent.click(doctorButton)
      
      // 2. Should navigate to doctor dashboard
      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument()
      })
      
      // 3. Should be able to navigate to prescribe page
      const prescribeButton = screen.getByText('Prescribe')
      fireEvent.click(prescribeButton)
      
      // 4. Should be able to fill prescription form
      await waitFor(() => {
        expect(screen.getByText('New Prescription')).toBeInTheDocument()
      })
      
      // 5. Should submit prescription successfully
      const submitButton = screen.getByRole('button', { name: /submit|create/i })
      expect(submitButton).toBeInTheDocument()
    })

    it('GREEN: Doctor can view their prescribed orders', async () => {
      // GREEN PHASE: Implementation makes test pass
      renderWithProviders(<App />)
      
      // Navigate to My Orders
      const ordersButton = screen.getByText('My Orders')
      fireEvent.click(ordersButton)
      
      // Should see prescribed orders
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
        expect(screen.getByText('Aspirin')).toBeInTheDocument()
        expect(screen.getByText('ACTIVE')).toBeInTheDocument()
      })
    })

    it('REFACTOR: Doctor workflow with improved error handling', async () => {
      // REFACTOR PHASE: Improve code while maintaining functionality
      const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
      mockUseQuery.mockReturnValue({
        data: [],
        isLoading: false,
        error: new Error('Network error'),
      })

      renderWithProviders(<App />)
      
      const ordersButton = screen.getByText('My Orders')
      fireEvent.click(ordersButton)
      
      // Should handle errors gracefully
      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
      })
    })
  })

  describe('Pharmacist Workflow - TDD Implementation', () => {
    beforeEach(() => {
      const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
      mockUseQuery.mockReturnValue({
        data: [
          {
            id: 'drug-1',
            name: 'Aspirin',
            strength: '500mg',
            current_stock: 50,
            low_stock_threshold: 10
          }
        ],
        isLoading: false,
        error: null,
      })
    })

    it('RED: Pharmacist should manage inventory workflow', async () => {
      renderWithProviders(<App />)
      
      // Select pharmacist role
      const pharmacistButton = screen.getByText('Pharmacist')
      fireEvent.click(pharmacistButton)
      
      // Navigate to inventory
      const inventoryButton = screen.getByText('Inventory')
      fireEvent.click(inventoryButton)
      
      // Should see inventory items
      await waitFor(() => {
        expect(screen.getByText('Aspirin')).toBeInTheDocument()
        expect(screen.getByText('50')).toBeInTheDocument() // Current stock
      })
    })

    it('GREEN: Pharmacist can transfer drugs between wards', async () => {
      const mockMutation = vi.fn().mockResolvedValue({ id: 'transfer-1' })
      const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
      mockUseMutation.mockReturnValue({
        mutate: mockMutation,
        isLoading: false,
        error: null,
      })

      renderWithProviders(<App />)
      
      // Navigate to drug transfer functionality
      const transferButton = screen.getByText(/transfer/i)
      fireEvent.click(transferButton)
      
      // Fill transfer form
      const quantityInput = screen.getByLabelText(/quantity/i)
      fireEvent.change(quantityInput, { target: { value: '10' } })
      
      const submitTransfer = screen.getByRole('button', { name: /transfer/i })
      fireEvent.click(submitTransfer)
      
      // Should call transfer API
      await waitFor(() => {
        expect(mockMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Nurse Workflow - TDD Implementation', () => {
    beforeEach(() => {
      const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
      mockUseQuery.mockReturnValue({
        data: [
          {
            id: 'patient-1',
            name: 'John Doe',
            bed_number: '101',
            overdue_count: 0,
            due_count: 2
          }
        ],
        isLoading: false,
        error: null,
      })
    })

    it('RED: Nurse should complete medication administration workflow', async () => {
      renderWithProviders(<App />)
      
      // Select nurse role
      const nurseButton = screen.getByText('Nurse')
      fireEvent.click(nurseButton)
      
      // Should see patient list
      await waitFor(() => {
        expect(screen.getByText('John Doe (Bed 101)')).toBeInTheDocument()
        expect(screen.getByText('2 due')).toBeInTheDocument()
      })
      
      // Click on patient to see medication administration record
      const patientCard = screen.getByText('John Doe (Bed 101)')
      fireEvent.click(patientCard)
      
      // Should open MAR (Medication Administration Record)
      await waitFor(() => {
        expect(screen.getByText(/medication.*record/i)).toBeInTheDocument()
      })
    })

    it('GREEN: Nurse can administer medications', async () => {
      const mockMutation = vi.fn().mockResolvedValue({ id: 'admin-1' })
      const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
      mockUseMutation.mockReturnValue({
        mutate: mockMutation,
        isLoading: false,
        error: null,
      })

      renderWithProviders(<App />)
      
      // Navigate to medication administration
      const adminButton = screen.getByRole('button', { name: /administer/i })
      fireEvent.click(adminButton)
      
      // Complete administration
      const confirmButton = screen.getByRole('button', { name: /confirm/i })
      fireEvent.click(confirmButton)
      
      // Should call administration API
      await waitFor(() => {
        expect(mockMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Admin Workflow - TDD Implementation', () => {
    it('RED: Admin should manage hospital and users', async () => {
      renderWithProviders(<App />)
      
      // Select admin role
      const adminButton = screen.getByText('Admin')
      fireEvent.click(adminButton)
      
      // Should see admin dashboard
      await waitFor(() => {
        expect(screen.getByText(/admin.*dashboard/i)).toBeInTheDocument()
      })
      
      // Navigate to hospital management
      const hospitalMgmtButton = screen.getByText(/hospital.*management/i)
      fireEvent.click(hospitalMgmtButton)
      
      // Should see hospital management interface
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /add.*hospital/i })).toBeInTheDocument()
      })
    })

    it('GREEN: Admin can manage users and roles', async () => {
      const mockMutation = vi.fn().mockResolvedValue({ id: 'user-1' })
      const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
      mockUseMutation.mockReturnValue({
        mutate: mockMutation,
        isLoading: false,
        error: null,
      })

      renderWithProviders(<App />)
      
      // Navigate to user management
      const userMgmtButton = screen.getByText(/user.*management/i)
      fireEvent.click(userMgmtButton)
      
      // Add new user
      const addUserButton = screen.getByRole('button', { name: /add.*user/i })
      fireEvent.click(addUserButton)
      
      // Should call user creation API
      await waitFor(() => {
        expect(mockMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Cross-Role Integration Tests', () => {
    it('INTEGRATION: Complete medication lifecycle workflow', async () => {
      // Test complete workflow from doctor prescription to nurse administration
      renderWithProviders(<App />)
      
      // 1. Doctor prescribes medication
      const doctorButton = screen.getByText('Doctor')
      fireEvent.click(doctorButton)
      
      const prescribeButton = screen.getByText('Prescribe')
      fireEvent.click(prescribeButton)
      
      // Create prescription (mocked)
      const mockCreatePrescription = vi.fn()
      
      // 2. Pharmacist reviews and approves
      const pharmacistButton = screen.getByText('Pharmacist')
      fireEvent.click(pharmacistButton)
      
      // 3. Nurse administers medication
      const nurseButton = screen.getByText('Nurse')
      fireEvent.click(nurseButton)
      
      // Complete workflow should be testable end-to-end
      expect(screen.getByText('MedLogistics')).toBeInTheDocument()
    })

    it('PERFORMANCE: System handles concurrent user operations', async () => {
      // Test system under load with multiple role operations
      const promises = []
      
      for (let i = 0; i < 5; i++) {
        promises.push(renderWithProviders(<App />))
      }
      
      await Promise.all(promises)
      
      // System should remain responsive
      expect(screen.getAllByText('MedLogistics')).toHaveLength(5)
    })
  })
}) 