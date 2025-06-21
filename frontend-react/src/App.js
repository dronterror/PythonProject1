import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Patients from './components/Patients';
import Drugs from './components/Drugs';
import Prescriptions from './components/Prescriptions';
import Analyses from './components/Analyses';
import Reports from './components/Reports';
import AuditLog from './components/AuditLog';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>ValMed</h1>
          </div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/patients" className="nav-link">Patients</Link>
            <Link to="/drugs" className="nav-link">Drugs</Link>
            <Link to="/prescriptions" className="nav-link">Prescriptions</Link>
            <Link to="/analyses" className="nav-link">Analyses</Link>
            <Link to="/reports" className="nav-link">Reports</Link>
            <Link to="/audit-log" className="nav-link">Audit Log</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/drugs" element={<Drugs />} />
            <Route path="/prescriptions" element={<Prescriptions />} />
            <Route path="/analyses" element={<Analyses />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/audit-log" element={<AuditLog />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 