import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from './utils'
import { BrowserRouter } from 'react-router-dom'
import MyOrdersPage from '../pages/doctor/MyOrdersPage'
import PrescribePage from '../pages/doctor/PrescribePage'
import HospitalManagementPage from '../pages/admin/HospitalManagementPage'
import UserManagementPage from '../pages/admin/UserManagementPage'

// Mock API client
vi.mock('@/lib/apiClient', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

// Mock React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  useQueryClient: vi.fn(),
}))

// Mock store
vi.mock('@/stores/useAppStore', () => ({
  useActiveWard: () => ({
    wardId: 'ward-123',
    wardName: 'Test Ward A',
  }),
}))

const renderWithRouter = (component: React.ReactNode) => {
  return renderWithProviders(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('MyOrdersPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state correctly', () => {
    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: true,
      error: null,
    })

    renderWithRouter(<MyOrdersPage />)
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('renders empty state when no orders', () => {
    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    })

    renderWithRouter(<MyOrdersPage />)
    
    expect(screen.getByText('No Orders Found')).toBeInTheDocument()
    expect(screen.getByText('You haven\'t prescribed any medications in this ward yet.')).toBeInTheDocument()
  })

  it('renders orders list correctly', () => {
    const mockOrders = [
      {
        id: 'order-1',
        patientName: 'John Doe',
        drugName: 'Aspirin',
        dosage: 500,
        status: 'active',
        createdAt: '2024-01-01T00:00:00Z',
        schedule: 'Every 8 hours',
      },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockOrders,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<MyOrdersPage />)
    
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Aspirin')).toBeInTheDocument()
    expect(screen.getByText('ACTIVE')).toBeInTheDocument()
  })

  it('handles error state correctly', () => {
    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: false,
      error: new Error('Failed to fetch'),
    })

    renderWithRouter(<MyOrdersPage />)
    
    expect(screen.getByText('Failed to load your orders. Please try again.')).toBeInTheDocument()
  })

  it('shows ward selection warning when no ward selected', () => {
    // Mock no ward selected
    vi.mocked(require('@/stores/useAppStore').useActiveWard).mockReturnValue({
      wardId: null,
      wardName: null,
    })

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    })

    renderWithRouter(<MyOrdersPage />)
    
    expect(screen.getByText('Please select a ward to view your orders.')).toBeInTheDocument()
  })

  it('opens order details dialog when order is clicked', async () => {
    const mockOrders = [
      {
        id: 'order-1',
        patientName: 'John Doe',
        drugName: 'Aspirin',
        dosage: 500,
        status: 'active',
        createdAt: '2024-01-01T00:00:00Z',
        schedule: 'Every 8 hours',
      },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockOrders,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<MyOrdersPage />)
    
    const orderCard = screen.getByText('John Doe').closest('[role="button"]')
    fireEvent.click(orderCard!)
    
    // Dialog should open (implementation dependent)
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })
})

describe('PrescribePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders prescription form correctly', () => {
    renderWithRouter(<PrescribePage />)
    
    expect(screen.getByText('New Prescription')).toBeInTheDocument()
    expect(screen.getByLabelText(/patient/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/medication/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/dosage/i)).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    renderWithRouter(<PrescribePage />)
    
    const submitButton = screen.getByRole('button', { name: /submit|create/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/patient.*required/i)).toBeInTheDocument()
    })
  })

  it('submits prescription successfully', async () => {
    const mockMutation = vi.fn().mockResolvedValue({ id: 'new-order-1' })
    const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
    mockUseMutation.mockReturnValue({
      mutate: mockMutation,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<PrescribePage />)
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/patient/i), {
      target: { value: 'Jane Doe' }
    })
    fireEvent.change(screen.getByLabelText(/dosage/i), {
      target: { value: '250' }
    })
    
    const submitButton = screen.getByRole('button', { name: /submit|create/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockMutation).toHaveBeenCalled()
    })
  })
})

describe('HospitalManagementPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders hospital management interface', () => {
    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    })

    renderWithRouter(<HospitalManagementPage />)
    
    expect(screen.getByText(/hospital.*management/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add.*hospital/i })).toBeInTheDocument()
  })

  it('handles hospital creation', async () => {
    const mockMutation = vi.fn()
    const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
    mockUseMutation.mockReturnValue({
      mutate: mockMutation,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<HospitalManagementPage />)
    
    const addButton = screen.getByRole('button', { name: /add.*hospital/i })
    fireEvent.click(addButton)
    
    // Should open dialog or form for adding hospital
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  it('displays hospitals list', () => {
    const mockHospitals = [
      { id: '1', name: 'General Hospital', location: 'Downtown' },
      { id: '2', name: 'Children Hospital', location: 'Uptown' },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockHospitals,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<HospitalManagementPage />)
    
    expect(screen.getByText('General Hospital')).toBeInTheDocument()
    expect(screen.getByText('Children Hospital')).toBeInTheDocument()
  })
})

describe('UserManagementPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders user management interface', () => {
    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    })

    renderWithRouter(<UserManagementPage />)
    
    expect(screen.getByText(/user.*management/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add.*user/i })).toBeInTheDocument()
  })

  it('displays users list with roles', () => {
    const mockUsers = [
      { id: '1', name: 'Dr. Smith', email: 'smith@hospital.com', role: 'doctor' },
      { id: '2', name: 'Nurse Jones', email: 'jones@hospital.com', role: 'nurse' },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockUsers,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<UserManagementPage />)
    
    expect(screen.getByText('Dr. Smith')).toBeInTheDocument()
    expect(screen.getByText('Nurse Jones')).toBeInTheDocument()
    expect(screen.getByText('doctor')).toBeInTheDocument()
    expect(screen.getByText('nurse')).toBeInTheDocument()
  })

  it('handles user role changes', async () => {
    const mockMutation = vi.fn()
    const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
    mockUseMutation.mockReturnValue({
      mutate: mockMutation,
      isLoading: false,
      error: null,
    })

    const mockUsers = [
      { id: '1', name: 'Dr. Smith', email: 'smith@hospital.com', role: 'doctor' },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockUsers,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<UserManagementPage />)
    
    // Click on user to edit role
    const userItem = screen.getByText('Dr. Smith').closest('tr')
    const editButton = userItem?.querySelector('[aria-label*="edit"]')
    
    if (editButton) {
      fireEvent.click(editButton)
      
      await waitFor(() => {
        expect(mockMutation).toHaveBeenCalled()
      })
    }
  })

  it('handles user deletion with confirmation', async () => {
    const mockMutation = vi.fn()
    const mockUseMutation = vi.mocked(require('@tanstack/react-query').useMutation)
    mockUseMutation.mockReturnValue({
      mutate: mockMutation,
      isLoading: false,
      error: null,
    })

    window.confirm = vi.fn().mockReturnValue(true)

    const mockUsers = [
      { id: '1', name: 'Dr. Smith', email: 'smith@hospital.com', role: 'doctor' },
    ]

    const mockUseQuery = vi.mocked(require('@tanstack/react-query').useQuery)
    mockUseQuery.mockReturnValue({
      data: mockUsers,
      isLoading: false,
      error: null,
    })

    renderWithRouter(<UserManagementPage />)
    
    const deleteButton = screen.getByRole('button', { name: /delete/i })
    fireEvent.click(deleteButton)
    
    expect(window.confirm).toHaveBeenCalledWith(
      expect.stringContaining('Are you sure')
    )
    
    await waitFor(() => {
      expect(mockMutation).toHaveBeenCalled()
    })
  })
}) 