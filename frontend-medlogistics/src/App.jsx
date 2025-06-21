import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NursePWA from './components/NursePWA.jsx';
import DoctorPWA from './components/DoctorPWA.jsx';
import PharmacyPWA from './components/PharmacyPWA.jsx';
import RoleSelector from './components/RoleSelector.jsx';
import './App.css';

function App() {
  const [selectedRole, setSelectedRole] = useState(null);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Role Selection Page */}
          <Route 
            path="/" 
            element={
              selectedRole ? (
                <Navigate to={`/${selectedRole}`} replace />
              ) : (
                <RoleSelector onRoleSelect={handleRoleSelect} />
              )
            } 
          />
          
          {/* PWA App Routes */}
          <Route path="/nurse" element={<NursePWA />} />
          <Route path="/doctor" element={<DoctorPWA />} />
          <Route path="/pharmacy" element={<PharmacyPWA />} />
          
          {/* Redirect to role selector if no role selected */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 