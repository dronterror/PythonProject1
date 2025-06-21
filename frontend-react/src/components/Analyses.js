import React, { useState, useEffect } from 'react';
import { analysesAPI, patientsAPI, drugsAPI } from '../services/api';
import './Analyses.css';

const Analyses = () => {
  const [analyses, setAnalyses] = useState([]);
  const [patients, setPatients] = useState([]);
  const [drugs, setDrugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingAnalysis, setEditingAnalysis] = useState(null);
  const [formData, setFormData] = useState({
    type: '',
    input_data: '',
    result: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [analysesRes, patientsRes, drugsRes] = await Promise.all([
        analysesAPI.getAll(),
        patientsAPI.getAll(),
        drugsAPI.getAll()
      ]);
      setAnalyses(Array.isArray(analysesRes.data) ? analysesRes.data : []);
      setPatients(Array.isArray(patientsRes.data) ? patientsRes.data : []);
      setDrugs(Array.isArray(drugsRes.data) ? drugsRes.data : []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error fetching data:', err);
      setAnalyses([]);
      setPatients([]);
      setDrugs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAnalysis) {
        await analysesAPI.update(editingAnalysis.id, formData);
      } else {
        await analysesAPI.create(formData);
      }
      setShowModal(false);
      setEditingAnalysis(null);
      resetForm();
      fetchData();
    } catch (err) {
      setError('Failed to save analysis');
      console.error('Error saving analysis:', err);
    }
  };

  const handleEdit = (analysis) => {
    setEditingAnalysis(analysis);
    setFormData({
      type: analysis.type || '',
      input_data: analysis.input_data || '',
      result: analysis.result || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try {
        await analysesAPI.delete(id);
        fetchData();
      } catch (err) {
        setError('Failed to delete analysis');
        console.error('Error deleting analysis:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      type: '',
      input_data: '',
      result: ''
    });
  };

  const openModal = () => {
    setShowModal(true);
    setEditingAnalysis(null);
    resetForm();
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingAnalysis(null);
    resetForm();
  };

  const getPatientName = (patientId) => {
    const patient = patients.find(p => p.id === patientId);
    return patient ? patient.name : 'Unknown';
  };

  const getDrugName = (drugId) => {
    const drug = drugs.find(d => d.id === drugId);
    return drug ? drug.name : 'Unknown';
  };

  if (loading) return <div className="loading">Loading analyses...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="analyses-container">
      <div className="header">
        <h2>Health Economic Analyses</h2>
        <button className="btn-primary" onClick={openModal}>
          Add New Analysis
        </button>
      </div>

      <div className="analyses-grid">
        {Array.isArray(analyses) && analyses.map((analysis) => (
          <div key={analysis.id} className="analysis-card">
            <div className="analysis-header">
              <h3>{analysis.type} Analysis #{analysis.id}</h3>
              <div className="analysis-actions">
                <button 
                  className="btn-edit" 
                  onClick={() => handleEdit(analysis)}
                >
                  Edit
                </button>
                <button 
                  className="btn-delete" 
                  onClick={() => handleDelete(analysis.id)}
                >
                  Delete
                </button>
              </div>
            </div>
            <div className="analysis-details">
              <p><strong>Type:</strong> {analysis.type}</p>
              <p><strong>Input Data:</strong> {analysis.input_data}</p>
              {analysis.result && (
                <p><strong>Result:</strong> {analysis.result}</p>
              )}
              <p><strong>Timestamp:</strong> {new Date(analysis.timestamp).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{editingAnalysis ? 'Edit Analysis' : 'Add New Analysis'}</h3>
              <button className="close-btn" onClick={closeModal}>×</button>
            </div>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label>Analysis Type:</label>
                <input
                  type="text"
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value})}
                  placeholder="e.g., ICER, QALY, Cost-Effectiveness"
                  required
                />
              </div>
              <div className="form-group">
                <label>Input Data:</label>
                <textarea
                  value={formData.input_data}
                  onChange={(e) => setFormData({...formData, input_data: e.target.value})}
                  placeholder="Enter analysis input data..."
                  required
                  rows="4"
                />
              </div>
              <div className="form-group">
                <label>Result (Optional):</label>
                <textarea
                  value={formData.result}
                  onChange={(e) => setFormData({...formData, result: e.target.value})}
                  placeholder="Enter analysis results..."
                  rows="4"
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">
                  {editingAnalysis ? 'Update Analysis' : 'Create Analysis'}
                </button>
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analyses; 