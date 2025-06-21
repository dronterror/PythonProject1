# ValMed Medication Logistics PWA

A dedicated Progressive Web App (PWA) for medication logistics management, designed as a mobile-first application for healthcare professionals.

## Features

### Role-Based Access
- **Nurse PWA**: Medication administration and patient care
- **Doctor PWA**: Prescription management and patient orders  
- **Pharmacist PWA**: Inventory management and stock alerts

### Mobile-First Design
- Responsive design optimized for mobile devices
- Touch-friendly interface
- PWA capabilities for native app installation
- Offline functionality support

### Key Components
- Role selector with intuitive navigation
- Real-time medication tracking
- Inventory management with alerts
- Patient medication administration
- Prescription creation and management

## Technology Stack

- **Frontend**: React 18 with hooks
- **Styling**: CSS3 with mobile-first responsive design
- **PWA**: Service workers and manifest for native app experience
- **Routing**: React Router for navigation
- **State Management**: React hooks (useState, useEffect)

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Docker (for containerized deployment)

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Access the application:**
   - Open http://localhost:3000
   - The app will automatically reload on file changes

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose build frontend-medlogistics
   docker-compose up frontend-medlogistics
   ```