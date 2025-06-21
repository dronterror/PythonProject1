import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Patients API
export const patientsAPI = {
  getAll: () => api.get('/patients'),
  getById: (id) => api.get(`/patients/${id}`),
  create: (data) => api.post('/dev/patients/', data),
  update: (id, data) => api.put(`/dev/patients/${id}`, data),
  delete: (id) => api.delete(`/dev/patients/${id}`),
};

// Drugs API
export const drugsAPI = {
  getAll: () => api.get('/drugs'),
  getById: (id) => api.get(`/drugs/${id}`),
  create: (data) => api.post('/dev/drugs/', data),
  update: (id, data) => api.put(`/dev/drugs/${id}`, data),
  delete: (id) => api.delete(`/dev/drugs/${id}`),
};

// Prescriptions API
export const prescriptionsAPI = {
  getAll: () => api.get('/prescriptions'),
  getById: (id) => api.get(`/prescriptions/${id}`),
  create: (data) => api.post('/dev/prescriptions/', data),
  update: (id, data) => api.put(`/dev/prescriptions/${id}`, data),
  delete: (id) => api.delete(`/dev/prescriptions/${id}`),
};

// Analyses API
export const analysesAPI = {
  getAll: () => api.get('/analyses'),
  getById: (id) => api.get(`/analyses/${id}`),
  create: (data) => api.post('/dev/analyses/', data),
  update: (id, data) => api.put(`/dev/analyses/${id}`, data),
  delete: (id) => api.delete(`/dev/analyses/${id}`),
  calculateICER: (data) => api.post('/analyses/calculate-icer', data),
};

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/dev/dashboard/metrics'),
  getTrends: () => api.get('/dev/dashboard/trends'),
};

// Reports API
export const reportsAPI = {
  getAll: () => api.get('/reports'),
  generatePatientSummary: () => api.post('/reports/generate/patient-summary'),
  generateDrugPerformance: () => api.post('/reports/generate/drug-performance'),
  generateFinancialAnalysis: () => api.post('/reports/generate/financial-analysis'),
  exportPatientsCSV: () => api.get('/export/patients/csv', { responseType: 'blob' }),
  exportDrugsCSV: () => api.get('/export/drugs/csv', { responseType: 'blob' }),
  exportPrescriptionsCSV: () => api.get('/export/prescriptions/csv', { responseType: 'blob' }),
  exportAllJSON: () => api.get('/export/all/json', { responseType: 'blob' }),
};

// Audit Log API
export const auditLogAPI = {
  getAll: () => api.get('/dev/audit-logs/'),
  getMyLogs: () => api.get('/dev/audit-logs/my-activity'),
};

export default api; 