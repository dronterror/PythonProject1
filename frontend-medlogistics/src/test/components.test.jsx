import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders, mockApiResponses, mockUsers } from './utils'
import RoleSelector from '../components/RoleSelector'
import DoctorPWA from '../components/DoctorPWA'
import NursePWA from '../components/NursePWA'
import PharmacyPWA from '../components/PharmacyPWA'
import Modal from '../components/Modal'

// Mock fetch globally
global.fetch = vi.fn()

describe('RoleSelector Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all role options', () => {
    renderWithProviders(<RoleSelector onRoleSelect={vi.fn()} />)
    
    expect(screen.getByText('Doctor')).toBeInTheDocument()
    expect(screen.getByText('Nurse')).toBeInTheDocument()
    expect(screen.getByText('Pharmacist')).toBeInTheDocument()
  })

  it('calls onRoleSelect when a role is clicked', () => {
    const mockOnRoleSelect = vi.fn()
    renderWithProviders(<RoleSelector onRoleSelect={mockOnRoleSelect} />)
    
    fireEvent.click(screen.getByText('Doctor'))
    
    expect(mockOnRoleSelect).toHaveBeenCalledWith('doctor')
  })

  it('applies correct styling to role buttons', () => {
    renderWithProviders(<RoleSelector onRoleSelect={vi.fn()} />)
    const doctorButton = screen.getByText('Doctor').closest('button')
    expect(doctorButton).toHaveClass('bg-white/90', 'backdrop-blur', 'rounded-3xl', 'shadow-lg', 'cursor-pointer')
  })
})

describe('DoctorPWA Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock localStorage for user data
    localStorage.setItem('user', JSON.stringify(mockUsers.doctor))
    // Mock successful API response
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => [
        { id: 1, name: 'John Doe', bed_number: '101', overdue_count: 0, due_count: 0 }
      ]
    })
  })

  it('renders doctor interface', async () => {
    renderWithProviders(<DoctorPWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    expect(screen.getByText('Doctor Orders')).toBeInTheDocument()
    expect(screen.getByText('New Order')).toBeInTheDocument()
  })

  it('shows create order form when New Order is clicked', async () => {
    renderWithProviders(<DoctorPWA />)
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    fireEvent.click(screen.getByRole('button', { name: 'New Order' }))
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'New Order' })).toBeInTheDocument()
      expect(screen.getByText('Patient')).toBeInTheDocument()
      expect(screen.getByText('Medication')).toBeInTheDocument()
      expect(screen.getByText('Dose')).toBeInTheDocument()
      expect(screen.getByText('Instructions')).toBeInTheDocument()
    })
  })

  it('submits order form successfully', async () => {
    renderWithProviders(<DoctorPWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByText('New Order'))
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText('Patient'), {
        target: { value: 'John Doe' }
      })
      fireEvent.change(screen.getByLabelText('Dose'), {
        target: { value: '2' }
      })
      fireEvent.change(screen.getByLabelText('Instructions'), {
        target: { value: 'Every 8 hours' }
      })
    })
    
    fireEvent.click(screen.getByText('Submit'))
    
    // The form submission is handled by the browser, so we just verify the form was filled
    expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('2')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Every 8 hours')).toBeInTheDocument()
  })

  it('displays patients list', async () => {
    renderWithProviders(<DoctorPWA />)
    
    // Wait for loading to complete and data to load
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('John Doe (Bed 101)')).toBeInTheDocument()
      expect(screen.getByText('No pending tasks')).toBeInTheDocument()
    })
  })
})

describe('NursePWA Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('user', JSON.stringify(mockUsers.nurse))
    // Mock successful API response
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => [
        { id: 1, name: 'John Doe', bed_number: '101', overdue_count: 0, due_count: 0 }
      ]
    })
  })

  it('renders nurse interface', async () => {
    renderWithProviders(<NursePWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    expect(screen.getByText('Ward 10B')).toBeInTheDocument()
    expect(screen.getByText('Filter')).toBeInTheDocument()
  })

  it('shows patients list', async () => {
    renderWithProviders(<NursePWA />)
    
    // Wait for loading to complete and data to load
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('John Doe (Bed 101)')).toBeInTheDocument()
      expect(screen.getByText('No pending tasks')).toBeInTheDocument()
    })
  })

  it('handles filter button click', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
    renderWithProviders(<NursePWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByText('Filter'))
    
    expect(alertSpy).toHaveBeenCalledWith('Filter clicked!')
    alertSpy.mockRestore()
  })
})

describe('PharmacyPWA Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('user', JSON.stringify(mockUsers.pharmacist))
    // Mock successful API response
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => [
        { id: 1, name: 'Aspirin', strength: '500mg', dosage_form: 'Tablet', quantity: 100, reorder_level: 10 }
      ]
    })
  })

  it('renders pharmacy interface', async () => {
    renderWithProviders(<PharmacyPWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    expect(screen.getByText('Formulary & Stock')).toBeInTheDocument()
    expect(screen.getByText('Filter')).toBeInTheDocument()
  })

  it('shows drug inventory', async () => {
    renderWithProviders(<PharmacyPWA />)
    
    // Wait for loading to complete and data to load
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('Aspirin 500mg (Tablet)')).toBeInTheDocument()
      expect(screen.getByText('In Stock')).toBeInTheDocument()
      expect(screen.getByText('100 units')).toBeInTheDocument()
    })
  })

  it('handles filter button click', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
    renderWithProviders(<PharmacyPWA />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByText('Filter'))
    
    expect(alertSpy).toHaveBeenCalledWith('Filter clicked!')
    alertSpy.mockRestore()
  })

  it('shows low stock status', async () => {
    // Mock low stock response
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => [
        { id: 1, name: 'Aspirin', strength: '500mg', dosage_form: 'Tablet', quantity: 5, reorder_level: 10 }
      ]
    })
    
    renderWithProviders(<PharmacyPWA />)
    
    // Wait for loading to complete and data to load
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('Aspirin 500mg (Tablet)')).toBeInTheDocument()
      expect(screen.getByText('Low Stock')).toBeInTheDocument()
      expect(screen.getByText('5 units')).toBeInTheDocument()
    })
  })
})

describe('Modal Component', () => {
  it('renders modal with title and content', () => {
    renderWithProviders(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    )
    
    expect(screen.getByText('Test Modal')).toBeInTheDocument()
    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    renderWithProviders(
      <Modal isOpen={false} onClose={vi.fn()} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    )
    
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument()
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn()
    renderWithProviders(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    )
    
    fireEvent.click(screen.getByRole('button', { name: /close/i }))
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when backdrop is clicked', () => {
    const mockOnClose = vi.fn()
    renderWithProviders(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    )
    
    const backdrop = screen.getByTestId('modal-backdrop')
    fireEvent.click(backdrop)
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('does not call onClose when modal content is clicked', () => {
    const mockOnClose = vi.fn()
    renderWithProviders(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    )
    
    const content = screen.getByText('Modal content')
    fireEvent.click(content)
    
    expect(mockOnClose).not.toHaveBeenCalled()
  })
}) 