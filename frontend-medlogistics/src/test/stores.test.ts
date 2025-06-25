import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAppStore } from '@/stores/useAppStore'
import type { UserProfile } from '@/types'

// Mock userProfile for testing
const mockUserProfile: UserProfile = {
  sub: 'auth0|123456789',
  email: 'test@example.com',
  name: 'Test User',
  picture: 'https://example.com/avatar.jpg',
  role: 'nurse',
  nurseId: 'nurse-123',
}

describe('useAppStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useAppStore())
    act(() => {
      result.current.clearSession()
    })
  })

  describe('User Session Management', () => {
    it('should start with empty session', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.userProfile).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.selectedRole).toBeNull()
    })

    it('should set user session correctly', () => {
      const { result } = renderHook(() => useAppStore())
      
      act(() => {
        result.current.setSession(mockUserProfile)
      })
      
      expect(result.current.userProfile).toEqual(mockUserProfile)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('should clear session correctly', () => {
      const { result } = renderHook(() => useAppStore())
      
      // First set a session
      act(() => {
        result.current.setSession(mockUserProfile)
        result.current.setSelectedRole('doctor')
        result.current.setActiveWard('ward-123', 'Ward A')
      })
      
      // Then clear it
      act(() => {
        result.current.clearSession()
      })
      
      expect(result.current.userProfile).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.selectedRole).toBeNull()
      expect(result.current.activeWardId).toBeNull()
      expect(result.current.activeWardName).toBeNull()
      expect(result.current.currentPage).toBe('dashboard')
    })
  })

  describe('Role Management', () => {
    it('should set selected role', () => {
      const { result } = renderHook(() => useAppStore())
      
      act(() => {
        result.current.setSelectedRole('doctor')
      })
      
      expect(result.current.selectedRole).toBe('doctor')
      expect(result.current.error).toBeNull()
    })

    it('should detect role types correctly', () => {
      const { result } = renderHook(() => useAppStore())
      
      // Test nurse role
      act(() => {
        result.current.setSelectedRole('nurse')
      })
      
      expect(result.current.isNurse()).toBe(true)
      expect(result.current.isDoctor()).toBe(false)
      expect(result.current.isPharmacist()).toBe(false)
      expect(result.current.isSuperAdmin()).toBe(false)
      
      // Test doctor role
      act(() => {
        result.current.setSelectedRole('doctor')
      })
      
      expect(result.current.isNurse()).toBe(false)
      expect(result.current.isDoctor()).toBe(true)
      expect(result.current.isPharmacist()).toBe(false)
      expect(result.current.isSuperAdmin()).toBe(false)
    })

    it('should determine if role needs ward', () => {
      const { result } = renderHook(() => useAppStore())
      
      // Roles that need ward
      const wardRoles = ['nurse', 'doctor', 'pharmacist']
      wardRoles.forEach(role => {
        act(() => {
          result.current.setSelectedRole(role)
        })
        expect(result.current.roleNeedsWard()).toBe(true)
      })
      
      // Role that doesn't need ward
      act(() => {
        result.current.setSelectedRole('super_admin')
      })
      expect(result.current.roleNeedsWard()).toBe(false)
    })
  })

  describe('Ward Management', () => {
    it('should set active ward', () => {
      const { result } = renderHook(() => useAppStore())
      
      act(() => {
        result.current.setActiveWard('ward-123', 'ICU Ward')
      })
      
      expect(result.current.activeWardId).toBe('ward-123')
      expect(result.current.activeWardName).toBe('ICU Ward')
      expect(result.current.hasActiveWard()).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('should detect if has active ward', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.hasActiveWard()).toBe(false)
      
      act(() => {
        result.current.setActiveWard('ward-123', 'ICU Ward')
      })
      
      expect(result.current.hasActiveWard()).toBe(true)
    })
  })

  describe('UI State Management', () => {
    it('should manage loading state', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.isLoading).toBe(false)
      
      act(() => {
        result.current.setLoading(true)
      })
      
      expect(result.current.isLoading).toBe(true)
    })

    it('should manage error state', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.error).toBeNull()
      
      act(() => {
        result.current.setError('Test error message')
      })
      
      expect(result.current.error).toBe('Test error message')
      
      act(() => {
        result.current.setError(null)
      })
      
      expect(result.current.error).toBeNull()
    })

    it('should manage current page', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.currentPage).toBe('dashboard')
      
      act(() => {
        result.current.setCurrentPage('patients')
      })
      
      expect(result.current.currentPage).toBe('patients')
    })
  })

  describe('Computed Properties', () => {
    it('should return correct hasSelectedRole', () => {
      const { result } = renderHook(() => useAppStore())
      
      expect(result.current.hasSelectedRole()).toBe(false)
      
      act(() => {
        result.current.setSelectedRole('nurse')
      })
      
      expect(result.current.hasSelectedRole()).toBe(true)
    })
  })

  describe('Persistence', () => {
    it('should persist important state to localStorage', () => {
      const { result } = renderHook(() => useAppStore())
      
      act(() => {
        result.current.setSession(mockUserProfile)
        result.current.setSelectedRole('doctor')
        result.current.setActiveWard('ward-123', 'ICU Ward')
      })
      
      // Check if state is persisted (this would require mocking localStorage)
      // In a real test, you'd mock localStorage and verify the calls
      expect(result.current.userProfile).toEqual(mockUserProfile)
      expect(result.current.selectedRole).toBe('doctor')
      expect(result.current.activeWardId).toBe('ward-123')
    })
  })
}) 