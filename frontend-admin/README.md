# MedLogistics Admin Frontend

Professional healthcare management platform admin interface built with React, TypeScript, Auth0, and Material-UI.

## Features

- **Auth0 Authentication**: Secure JWT-based authentication
- **Super Admin Access Control**: Role-based access to admin features
- **Hospital Management**: Create and manage hospital entities
- **User Management**: Invite users and assign them to hospitals/wards
- **Responsive Design**: Modern Material-UI interface that works on all devices

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Auth0 account configured with:
  - Single Page Application for frontend
  - API for backend
  - Machine-to-Machine application for user management

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-auth0-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_API_AUDIENCE=https://api.medlogistics.com

# API Configuration  
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Auth0 Configuration

#### Single Page Application Settings:
- **Allowed Callback URLs**: `http://localhost:3000`
- **Allowed Logout URLs**: `http://localhost:3000`
- **Allowed Web Origins**: `http://localhost:3000`
- **Allowed Origins (CORS)**: `http://localhost:3000`

#### API Settings:
- **Identifier**: `https://api.medlogistics.com`
- **Signing Algorithm**: `RS256`

#### Custom Claims (Rules/Actions):
Add custom claims to include user roles in the token:

```javascript
// Auth0 Rule/Action to add custom claims
function addCustomClaims(user, context, callback) {
  const namespace = 'https://api.medlogistics.com/';
  context.accessToken[namespace + 'roles'] = user.app_metadata?.roles || [];
  callback(null, user, context);
}
```

### 4. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── LoginButton.tsx  # Auth0 login component
│   ├── LogoutButton.tsx # Auth0 logout component
│   └── Profile.tsx      # User profile display
├── pages/               # Main application pages
│   ├── HospitalManagement.tsx  # Hospital CRUD operations
│   └── UserManagement.tsx      # User invite and management
├── App.tsx             # Main application component
└── main.tsx           # Application entry point
```

## User Roles

The application supports the following roles:

- **super_admin**: Full access to all admin features
- **doctor**: Medical staff role
- **nurse**: Nursing staff role  
- **pharmacist**: Pharmacy staff role

> **Note**: Only users with the `super_admin` role can access this admin interface.

## API Integration

The frontend integrates with the backend API endpoints:

- `GET /api/admin/hospitals` - List hospitals
- `POST /api/admin/hospitals` - Create hospital
- `GET /api/admin/hospitals/{id}/wards` - List wards for hospital
- `POST /api/admin/hospitals/{id}/wards` - Create ward
- `GET /api/admin/users` - List users
- `POST /api/admin/users/invite` - Invite new user

All API calls include JWT authentication tokens in the Authorization header.

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **Auth0 React SDK** - Authentication
- **React Router** - Client-side routing
- **MUI X DataGrid** - Advanced data tables

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Adding New Features

1. Create new components in `src/components/`
2. Create new pages in `src/pages/`
3. Add routes in `App.tsx`
4. Update navigation in the drawer component

## Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables for Production

Update your `.env` file with production values:

```env
VITE_AUTH0_DOMAIN=your-production-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-production-client-id
VITE_AUTH0_API_AUDIENCE=https://api.medlogistics.com
VITE_API_BASE_URL=https://your-api-domain.com
```

### Deployment Checklist

- [ ] Update Auth0 allowed URLs for production domain
- [ ] Configure CORS in backend for production domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure environment variables
- [ ] Test authentication flow in production

## Security Considerations

- All routes require authentication
- Super admin role required for access
- JWT tokens are automatically refreshed
- API requests include proper authorization headers
- Sensitive operations require additional confirmation

## Troubleshooting

### Common Issues

1. **Auth0 Configuration Error**: Verify all Auth0 settings match your configuration
2. **CORS Issues**: Ensure backend allows the frontend domain
3. **Role Access Denied**: Verify the user has `super_admin` role in Auth0
4. **API Connection Failed**: Check API base URL and backend status

### Debug Mode

Enable debug logging by adding to your `.env`:

```env
VITE_DEBUG=true
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Auth0 and MUI documentation
3. Check backend API logs for authentication issues
