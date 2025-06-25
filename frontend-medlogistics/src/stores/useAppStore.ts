import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { UserProfile } from '@/types';

interface AppState {
  // User session state
  userProfile: UserProfile | null;
  isAuthenticated: boolean;
  
  // Role selection state
  selectedRole: string | null;
  
  // Ward context state
  activeWardId: string | null;
  activeWardName: string | null;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Navigation state
  currentPage: string;
  
  // Actions
  setSession: (userProfile: UserProfile) => void;
  setSelectedRole: (role: string) => void;
  setActiveWard: (wardId: string, wardName: string) => void;
  clearSession: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCurrentPage: (page: string) => void;
  
  // Computed getters
  hasActiveWard: () => boolean;
  hasSelectedRole: () => boolean;
  isNurse: () => boolean;
  isDoctor: () => boolean;
  isPharmacist: () => boolean;
  isSuperAdmin: () => boolean;
  roleNeedsWard: () => boolean;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        userProfile: null,
        isAuthenticated: false,
        selectedRole: null,
        activeWardId: null,
        activeWardName: null,
        isLoading: false,
        error: null,
        currentPage: 'dashboard',
        
        // Actions
        setSession: (userProfile: UserProfile) => {
          set(
            {
              userProfile,
              isAuthenticated: true,
              error: null,
            },
            false,
            'setSession'
          );
        },
        
        setSelectedRole: (role: string) => {
          set(
            {
              selectedRole: role,
              error: null,
            },
            false,
            'setSelectedRole'
          );
        },
        
        setActiveWard: (wardId: string, wardName: string) => {
          set(
            {
              activeWardId: wardId,
              activeWardName: wardName,
              error: null,
            },
            false,
            'setActiveWard'
          );
        },
        
        clearSession: () => {
          set(
            {
              userProfile: null,
              isAuthenticated: false,
              selectedRole: null,
              activeWardId: null,
              activeWardName: null,
              currentPage: 'dashboard',
              error: null,
            },
            false,
            'clearSession'
          );
        },
        
        setLoading: (loading: boolean) => {
          set({ isLoading: loading }, false, 'setLoading');
        },
        
        setError: (error: string | null) => {
          set({ error }, false, 'setError');
        },
        
        setCurrentPage: (page: string) => {
          set({ currentPage: page }, false, 'setCurrentPage');
        },
        
        // Computed getters
        hasActiveWard: () => {
          const state = get();
          return state.activeWardId !== null;
        },
        
        hasSelectedRole: () => {
          const state = get();
          return state.selectedRole !== null;
        },
        
        isNurse: () => {
          const state = get();
          return state.selectedRole === 'nurse';
        },
        
        isDoctor: () => {
          const state = get();
          return state.selectedRole === 'doctor';
        },
        
        isPharmacist: () => {
          const state = get();
          return state.selectedRole === 'pharmacist';
        },
        
        isSuperAdmin: () => {
          const state = get();
          return state.selectedRole === 'super_admin';
        },
        
        roleNeedsWard: () => {
          const state = get();
          return Boolean(state.selectedRole && ['nurse', 'doctor', 'pharmacist'].includes(state.selectedRole));
        },
      }),
      {
        name: 'medlog-nurse-app-store',
        partialize: (state) => ({
          userProfile: state.userProfile,
          isAuthenticated: state.isAuthenticated,
          selectedRole: state.selectedRole,
          activeWardId: state.activeWardId,
          activeWardName: state.activeWardName,
        }),
      }
    ),
    {
      name: 'MedLog Nurse App Store',
    }
  )
);

// Selector hooks for better performance
export const useUserProfile = () => useAppStore((state) => state.userProfile);
export const useActiveWard = () => useAppStore((state) => ({
  wardId: state.activeWardId,
  wardName: state.activeWardName,
}));
export const useSelectedRole = () => useAppStore((state) => state.selectedRole);
export const useAuthState = () => useAppStore((state) => ({
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
  error: state.error,
}));
export const useUIState = () => useAppStore((state) => ({
  currentPage: state.currentPage,
  isLoading: state.isLoading,
  error: state.error,
})); 