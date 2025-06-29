import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { UserProfile, Ward } from '@/types';

interface AppState {
  // User session state
  userProfile: UserProfile | null;
  
  // Active ward state
  activeWard: Ward | null;

  // Actions
  setSession: (userProfile: UserProfile, roles: string[]) => void;
  setActiveWard: (ward: Ward) => void;
  clearSession: () => void;
  
  // UI state
  isLoading: boolean;
  error: string | null;

  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        userProfile: null,
        activeWard: null,
        isLoading: false,
        error: null,
        
        // Actions
        setSession: (userProfile: UserProfile, roles: string[]) => {
          set(
            {
              userProfile: { ...userProfile, roles },
              error: null,
            },
            false,
            'setSession'
          );
        },
        
        setActiveWard: (ward: Ward) => {
          set(
            {
              activeWard: ward,
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
              activeWard: null,
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
      }),
      {
        name: 'medlog-pwa-store', // Updated store name
        partialize: (state) => ({
          userProfile: state.userProfile,
          activeWard: state.activeWard,
        }),
      }
    ),
    {
      name: 'MedLog PWA Store', // Updated devtools name
    }
  )
);

// Selector hooks for better performance
export const useUser = () => useAppStore((state) => state.userProfile);
export const useActiveWard = () => useAppStore((state) => state.activeWard);
export const useSession = () => useAppStore((state) => ({
    userProfile: state.userProfile,
    activeWard: state.activeWard,
}));
export const useUIState = () => useAppStore((state) => ({
  isLoading: state.isLoading,
  error: state.error,
})); 