# MedLog Nurse PWA

A modern, mobile-first Progressive Web Application for nurses to manage medication administration and patient care.

## 🏗️ Architecture

### Tech Stack

- **Framework**: React 18 with TypeScript and Vite
- **UI Library**: Material-UI (MUI) v5 - Mobile-optimized components
- **Routing**: React Router DOM v6
- **State Management**: Zustand with persistence
- **Data Fetching**: TanStack Query (React Query) with optimistic updates
- **Authentication**: Auth0 React SDK
- **PWA**: Vite PWA Plugin with Workbox
- **Styling**: MUI styled-components with mobile-first theme

### Key Features

- 🔐 **Secure Authentication**: Auth0 integration with JWT tokens
- 🏥 **Ward Context**: Automatic ward-based API calls and filtering
- 📱 **Mobile-First Design**: Optimized for tablets and mobile devices
- 🔄 **Offline Support**: PWA with intelligent caching strategies
- ⚡ **Fast Performance**: Optimized queries and state management
- 🎨 **Professional UI**: Medical-grade interface with accessibility

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Access to the MedLog API backend
- Auth0 account and application configuration

### Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Setup**
   Create a `.env` file with your configuration:
   ```env
   VITE_API_BASE_URL=http://localhost/api
   VITE_AUTH0_DOMAIN=your-auth0-domain
   VITE_AUTH0_CLIENT_ID=your-auth0-client-id
   VITE_AUTH0_AUDIENCE=https://api.medlog.app
   ```

3. **Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

## 📱 Application Flow

### Authentication Flow
1. **Login**: Auth0 hosted login page
2. **Token Management**: Automatic JWT token handling
3. **Ward Selection**: Choose active ward for session context
4. **Main Application**: Full access to nurse dashboard

### Ward Context System
- Every API call automatically includes the active ward ID
- Ward selection persists across sessions
- Easy ward switching without re-authentication

### Core Navigation
- **Dashboard**: Overview of pending medications and activities
- **Patients**: Ward-specific patient list with status indicators
- **Medications**: Medication administration records (MAR)
- **Profile**: User settings and preferences

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── layout/         # Layout components (NurseLayout)
│   └── ward/           # Ward selection components
├── lib/                # Utilities and configurations
│   └── apiClient.ts    # Axios instance with auth/ward interceptors
├── pages/              # Page components
│   ├── DashboardPage.tsx
│   └── PatientsPage.tsx
├── stores/             # Zustand state management
│   └── useAppStore.ts  # Main application store
├── theme/              # MUI theme configuration
│   └── index.ts        # Mobile-first theme
├── types/              # TypeScript type definitions
│   └── index.ts        # Application types
├── App.tsx             # Main application component
└── main.tsx            # Application entry point
```

## 🔧 State Management

### Zustand Store (`useAppStore`)

**Session State:**
- `userProfile`: Auth0 user information and role
- `isAuthenticated`: Authentication status

**Ward Context:**
- `activeWardId`: Currently selected ward ID
- `activeWardName`: Ward display name

**UI State:**
- `isLoading`: Global loading state
- `error`: Error messages
- `currentPage`: Navigation state

### Selector Hooks
```typescript
const userProfile = useUserProfile();
const { wardId, wardName } = useActiveWard();
const { isAuthenticated, isLoading } = useAuthState();
```

## 🌐 API Integration

### Automatic Context Injection
The API client automatically adds:
- **Authorization Header**: `Bearer ${jwt_token}`
- **Ward Context Header**: `X-Ward-ID: ${activeWardId}`
- **Request Timestamp**: For debugging and caching

### Error Handling
- **401 Unauthorized**: Automatic logout trigger
- **403 Forbidden**: Permission error display
- **Network Errors**: Offline-friendly error messages
- **Validation Errors**: User-friendly form feedback

### Caching Strategy
- **Stale While Revalidate**: API responses cached for 5 minutes
- **Background Sync**: Updates when connection restored
- **Optimistic Updates**: Immediate UI feedback for mutations

## 📱 PWA Features

### Offline Support
- **App Shell**: Core application cached for offline use
- **API Caching**: Recent data available offline
- **Background Sync**: Queued actions when online

### Installation
- **Add to Home Screen**: Native app-like experience
- **App Icons**: Professional medical branding
- **Splash Screen**: Branded loading experience

### Performance
- **Code Splitting**: Route-based lazy loading
- **Tree Shaking**: Minimal bundle size
- **Service Worker**: Intelligent caching and updates

## 🎨 Design System

### Mobile-First Theme
- **Breakpoints**: Optimized for tablets (768px+) and phones
- **Touch Targets**: Minimum 48px for accessibility
- **Typography**: Readable font sizes and line heights
- **Colors**: Medical-grade color palette with high contrast

### Component Customizations
- **Bottom Navigation**: Primary navigation for mobile
- **App Bar**: Context-aware header with ward display
- **Cards**: Elevated design with proper spacing
- **Forms**: Large touch-friendly inputs

## 🔒 Security

### Authentication
- **Auth0 Integration**: Industry-standard OAuth 2.0/OIDC
- **JWT Tokens**: Secure API authentication
- **Refresh Tokens**: Automatic token renewal
- **Secure Storage**: LocalStorage with encryption

### Authorization
- **Role-Based Access**: Nurse-specific permissions
- **Ward Context**: Data isolation by ward
- **API Security**: All requests authenticated and authorized

## 🧪 Development

### Available Scripts
- `npm run dev`: Development server with hot reload
- `npm run build`: Production build with optimization
- `npm run preview`: Preview production build locally
- `npm run lint`: ESLint code quality checks
- `npm run test`: Run test suite (when implemented)

### Development Tools
- **React Query Devtools**: API state inspection
- **Zustand Devtools**: State management debugging
- **TypeScript**: Full type safety and IntelliSense
- **Vite HMR**: Fast development reload

### Code Quality
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code style and error detection
- **Prettier**: Consistent code formatting
- **Path Mapping**: Clean imports with `@/` prefix

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Support
The application includes Docker configuration for containerized deployment.

### Environment Variables
Ensure all required environment variables are set for production:
- Auth0 configuration
- API endpoint URLs
- Application environment settings

## 📈 Performance

### Optimization Features
- **Bundle Splitting**: Route-based code splitting
- **Tree Shaking**: Unused code elimination
- **Image Optimization**: Responsive images with proper formats
- **Caching**: Intelligent service worker caching
- **Lazy Loading**: Components loaded on demand

### Mobile Performance
- **Touch Optimization**: Fast touch response
- **Network Resilience**: Works on slow connections
- **Battery Efficiency**: Optimized for mobile devices
- **Memory Management**: Efficient state and component lifecycle

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `npm install`
3. Copy environment variables: `cp .env.example .env`
4. Start development server: `npm run dev`

### Code Standards
- Follow TypeScript strict mode
- Use MUI components and theme system
- Implement proper error boundaries
- Write mobile-first responsive code
- Follow React Query patterns for data fetching

## 📄 License

This project is part of the MedLog healthcare management system.