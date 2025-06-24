import { createTheme, ThemeOptions } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// Color palette specifically designed for medical applications
const palette = {
  primary: {
    main: '#1976d2', // Professional blue
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#26a69a', // Medical teal
    light: '#4db6ac',
    dark: '#00695c',
    contrastText: '#ffffff',
  },
  error: {
    main: '#d32f2f', // Critical alerts
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02', // Warnings
    light: '#ff9800',
    dark: '#e65100',
  },
  success: {
    main: '#2e7d32', // Success states
    light: '#4caf50',
    dark: '#1b5e20',
  },
  info: {
    main: '#0288d1', // Information
    light: '#03a9f4',
    dark: '#01579b',
  },
  background: {
    default: '#f8f9fa',
    paper: '#ffffff',
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
  },
};

// Typography optimized for mobile reading
const typography = {
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2rem',
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '1.75rem',
    fontWeight: 500,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.43,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.66,
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    textTransform: 'none' as const,
  },
};

// Component customizations for mobile-first design
const components = {
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0px 2px 4px rgba(0,0,0,0.1)',
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0px 2px 8px rgba(0,0,0,0.1)',
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '12px 24px',
        fontSize: '1rem',
        minHeight: 48, // Minimum touch target size
      },
      contained: {
        boxShadow: '0px 2px 4px rgba(0,0,0,0.2)',
        '&:hover': {
          boxShadow: '0px 4px 8px rgba(0,0,0,0.3)',
        },
      },
    },
  },
  MuiFab: {
    styleOverrides: {
      root: {
        width: 56,
        height: 56,
      },
    },
  },
  MuiBottomNavigation: {
    styleOverrides: {
      root: {
        height: 70,
        boxShadow: '0px -2px 8px rgba(0,0,0,0.1)',
      },
    },
  },
  MuiBottomNavigationAction: {
    styleOverrides: {
      root: {
        minWidth: 'auto',
        padding: '8px 12px',
        '&.Mui-selected': {
          paddingTop: 8,
        },
      },
      label: {
        fontSize: '0.75rem',
        '&.Mui-selected': {
          fontSize: '0.75rem',
        },
      },
    },
  },
  MuiListItem: {
    styleOverrides: {
      root: {
        minHeight: 56, // Comfortable touch targets
        borderRadius: 8,
        marginBottom: 4,
      },
    },
  },
  MuiListItemButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        minHeight: 56,
        '&:hover': {
          backgroundColor: alpha(palette.primary.main, 0.04),
        },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        height: 32,
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
        },
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 16,
        margin: 16,
        width: 'calc(100% - 32px)',
        maxHeight: 'calc(100% - 32px)',
      },
    },
  },
  MuiSnackbar: {
    styleOverrides: {
      root: {
        bottom: 90, // Above bottom navigation
      },
    },
  },
};

// Breakpoints optimized for mobile devices
const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 900,
    lg: 1200,
    xl: 1536,
  },
};

// Spacing system
const spacing = 8;

const themeOptions: ThemeOptions = {
  palette,
  typography,
  components,
  breakpoints,
  spacing,
  shape: {
    borderRadius: 8,
  },
};

export const theme = createTheme(themeOptions);

// Export individual theme parts for use in styled components
export { palette, typography, components, breakpoints, spacing }; 