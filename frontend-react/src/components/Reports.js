import React, { useState, useEffect } from 'react';
import { reportsAPI } from '../services/api';
import './Reports.css';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await reportsAPI.getAll();
      setReports(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch reports');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setGenerating(true);
      let response;
      
      switch (reportType) {
        case 'patient-summary':
          response = await reportsAPI.generatePatientSummary();
          break;
        case 'drug-performance':
          response = await reportsAPI.generateDrugPerformance();
          break;
        case 'financial-analysis':
          response = await reportsAPI.generateFinancialAnalysis();
          break;
        default:
          throw new Error('Unknown report type');
      }
      
      alert(`Report generated successfully! Report ID: ${response.data.report_id}`);
      fetchReports();
    } catch (err) {
      setError(`Failed to generate ${reportType} report`);
      console.error('Error generating report:', err);
    } finally {
      setGenerating(false);
    }
  };

  const exportData = async (exportType) => {
    try {
      let response;
      
      switch (exportType) {
        case 'patients-csv':
          response = await reportsAPI.exportPatientsCSV();
          break;
        case 'drugs-csv':
          response = await reportsAPI.exportDrugsCSV();
          break;
        case 'prescriptions-csv':
          response = await reportsAPI.exportPrescriptionsCSV();
          break;
        case 'all-json':
          response = await reportsAPI.exportAllJSON();
          break;
        default:
          throw new Error('Unknown export type');
      }
      
      // Create download link
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exportType}-${new Date().toISOString().split('T')[0]}.${exportType.includes('json') ? 'json' : 'csv'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (err) {
      setError(`Failed to export ${exportType}`);
      console.error('Error exporting data:', err);
    }
  };

  if (loading) return <div className="loading">Loading reports...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="reports-container">
      <div className="header">
        <h2>Reports & Analytics</h2>
      </div>

      <div className="reports-sections">
        {/* Report Generation */}
        <div className="section">
          <h3>Generate Reports</h3>
          <div className="report-actions">
            <button 
              className="btn-primary"
              onClick={() => generateReport('patient-summary')}
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Patient Summary'}
            </button>
            <button 
              className="btn-primary"
              onClick={() => generateReport('drug-performance')}
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Drug Performance'}
            </button>
            <button 
              className="btn-primary"
              onClick={() => generateReport('financial-analysis')}
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Financial Analysis'}
            </button>
          </div>
        </div>

        {/* Data Export */}
        <div className="section">
          <h3>Export Data</h3>
          <div className="export-actions">
            <button 
              className="btn-secondary"
              onClick={() => exportData('patients-csv')}
            >
              Export Patients (CSV)
            </button>
            <button 
              className="btn-secondary"
              onClick={() => exportData('drugs-csv')}
            >
              Export Drugs (CSV)
            </button>
            <button 
              className="btn-secondary"
              onClick={() => exportData('prescriptions-csv')}
            >
              Export Prescriptions (CSV)
            </button>
            <button 
              className="btn-secondary"
              onClick={() => exportData('all-json')}
            >
              Export All Data (JSON)
            </button>
          </div>
        </div>

        {/* Generated Reports */}
        <div className="section">
          <h3>Generated Reports</h3>
          <div className="reports-list">
            {reports.length === 0 ? (
              <p className="no-reports">No reports generated yet. Use the buttons above to generate reports.</p>
            ) : (
              reports.map((report) => (
                <div key={report.id} className="report-item">
                  <div className="report-info">
                    <h4>{report.title}</h4>
                    <p><strong>Created:</strong> {new Date(report.created_at).toLocaleDateString()}</p>
                    <p><strong>Type:</strong> {report.report_type || 'General'}</p>
                  </div>
                  <div className="report-actions">
                    <button 
                      className="btn-view"
                      onClick={() => alert(report.content)}
                    >
                      View Content
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports; 