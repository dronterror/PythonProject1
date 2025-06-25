import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from './utils'
import DoctorLayout from '../components/layout/DoctorLayout'
import PharmacistLayout from '../components/layout/PharmacistLayout'
import { BrowserRouter } from 'react-router-dom'

// Mock Auth0
vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    logout: vi.fn(),
  }),
}))

// Mock the store
vi.mock('@/stores/useAppStore', () => ({
  useAppStore: () => ({
    clearSession: vi.fn(),
  }),
  useActiveWard: () => ({
    wardName: 'Test Ward A',
    wardId: 'ward-123',
  }),
  useUserProfile: () => ({
    name: 'Dr. Test User',
    picture: 'https://example.com/avatar.jpg',
  }),
}))

const renderWithRouter = (component: React.ReactNode) => {
  return renderWithProviders(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('DoctorLayout Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders doctor navigation correctly', () => {
    renderWithRouter(<DoctorLayout />)
    
    // Should show main navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('My Orders')).toBeInTheDocument()
    expect(screen.getByText('Prescribe')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  it('displays user profile information', () => {
    renderWithRouter(<DoctorLayout />)
    
    expect(screen.getByText('Dr. Test User')).toBeInTheDocument()
    expect(screen.getByText('Doctor')).toBeInTheDocument()
  })

  it('shows active ward information', () => {
    renderWithRouter(<DoctorLayout />)
    
    expect(screen.getByText('Test Ward A')).toBeInTheDocument()
    expect(screen.getByText('Click to change')).toBeInTheDocument()
  })

  it('handles navigation menu toggle on mobile', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 500,
    })

    renderWithRouter(<DoctorLayout />)
    
    const menuButton = screen.getByLabelText(/menu/i)
    expect(menuButton).toBeInTheDocument()
  })

  it('calls logout function when logout is clicked', async () => {
    const mockLogout = vi.fn()
    vi.mocked(require('@auth0/auth0-react').useAuth0).mockReturnValue({
      logout: mockLogout,
    })

    renderWithRouter(<DoctorLayout />)
    
    const logoutButton = screen.getByText('Logout')
    fireEvent.click(logoutButton)
    
    expect(mockLogout).toHaveBeenCalledWith({
      logoutParams: {
        returnTo: window.location.origin,
      },
    })
  })

  it('highlights active navigation item', () => {
    // Mock current location
    delete (window as any).location
    window.location = { ...window.location, pathname: '/app/orders' }

    renderWithRouter(<DoctorLayout />)
    
    const ordersButton = screen.getByText('My Orders').closest('button')
    expect(ordersButton).toHaveClass('Mui-selected')
  })
})

describe('PharmacistLayout Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders pharmacist navigation correctly', () => {
    renderWithRouter(<PharmacistLayout />)
    
    // Should show pharmacist-specific navigation
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Inventory')).toBeInTheDocument()
    expect(screen.getByText('Alerts')).toBeInTheDocument()
  })

  it('displays correct role in user info', () => {
    renderWithRouter(<PharmacistLayout />)
    
    expect(screen.getByText('Pharmacist')).toBeInTheDocument()
  })

  it('handles ward selector functionality', () => {
    renderWithRouter(<PharmacistLayout />)
    
    const wardSelector = screen.getByText('Test Ward A')
    fireEvent.click(wardSelector)
    
    // Should trigger navigation to ward selector
    // This would be tested with a mock router
  })
}) 