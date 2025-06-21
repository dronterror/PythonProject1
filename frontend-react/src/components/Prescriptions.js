import React, { useState, useEffect } from 'react';
import { prescriptionsAPI, patientsAPI, drugsAPI } from '../services/api';
import './Prescriptions.css';

const Prescriptions = () => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [patients, setPatients] = useState([]);
  const [drugs, setDrugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingPrescription, setEditingPrescription] = useState(null);
  const [formData, setFormData] = useState({
    patient_id: '',
    drug_id: '',
    dosage: '',
    frequency: '',
    duration: '',
    cost_at_time_of_prescription: '',
    effectiveness_at_time_of_prescription: '',
    qaly_score: '',
    prescription_date: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [prescriptionsRes, patientsRes, drugsRes] = await Promise.all([
        prescriptionsAPI.getAll(),
        patientsAPI.getAll(),
        drugsAPI.getAll()
      ]);
      setPrescriptions(prescriptionsRes.data);
      setPatients(patientsRes.data);
      setDrugs(drugsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingPrescription) {
        await prescriptionsAPI.update(editingPrescription.id, formData);
      } else {
        await prescriptionsAPI.create(formData);
      }
      setShowModal(false);
      setEditingPrescription(null);
      resetForm();
      fetchData();
    } catch (err) {
      setError('Failed to save prescription');
      console.error('Error saving prescription:', err);
    }
  };

  const handleEdit = (prescription) => {
    setEditingPrescription(prescription);
    setFormData({
      patient_id: prescription.patient_id,
      drug_id: prescription.drug_id,
      dosage: prescription.dosage,
      frequency: prescription.frequency,
      duration: prescription.duration,
      cost_at_time_of_prescription: prescription.cost_at_time_of_prescription,
      effectiveness_at_time_of_prescription: prescription.effectiveness_at_time_of_prescription,
      qaly_score: prescription.qaly_score,
      prescription_date: prescription.prescription_date
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this prescription?')) {
      try {
        await prescriptionsAPI.delete(id);
        fetchData();
      } catch (err) {
        setError('Failed to delete prescription');
        console.error('Error deleting prescription:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      patient_id: '',
      drug_id: '',
      dosage: '',
      frequency: '',
      duration: '',
      cost_at_time_of_prescription: '',
      effectiveness_at_time_of_prescription: '',
      qaly_score: '',
      prescription_date: ''
    });
  };

  const openModal = () => {
    setShowModal(true);
    setEditingPrescription(null);
    resetForm();
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingPrescription(null);
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

  if (loading) return <div className="loading">Loading prescriptions...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="prescriptions-container">
      <div className="header">
        <h2>Prescription Management</h2>
        <button className="btn-primary" onClick={openModal}>
          Add New Prescription
        </button>
      </div>

      <div className="prescriptions-grid">
        {prescriptions.map((prescription) => (
          <div key={prescription.id} className="prescription-card">
            <div className="prescription-header">
              <h3>Prescription #{prescription.id}</h3>
              <div className="prescription-actions">
                <button 
                  className="btn-edit" 
                  onClick={() => handleEdit(prescription)}
                >
                  Edit
                </button>
                <button 
                  className="btn-delete" 
                  onClick={() => handleDelete(prescription.id)}
                >
                  Delete
                </button>
              </div>
            </div>
            <div className="prescription-details">
              <p><strong>Patient:</strong> {getPatientName(prescription.patient_id)}</p>
              <p><strong>Drug:</strong> {getDrugName(prescription.drug_id)}</p>
              <p><strong>Dosage:</strong> {prescription.dosage}</p>
              <p><strong>Frequency:</strong> {prescription.frequency}</p>
              <p><strong>Duration:</strong> {prescription.duration}</p>
              <p><strong>Cost:</strong> ${prescription.cost_at_time_of_prescription}</p>
              <p><strong>Effectiveness:</strong> {prescription.effectiveness_at_time_of_prescription}</p>
              <p><strong>QALY Score:</strong> {prescription.qaly_score}</p>
              <p><strong>Date:</strong> {prescription.prescription_date}</p>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{editingPrescription ? 'Edit Prescription' : 'Add New Prescription'}</h3>
              <button className="close-btn" onClick={closeModal}>×</button>
            </div>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label>Patient:</label>
                <select
                  value={formData.patient_id}
                  onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  required
                >
                  <option value="">Select Patient</option>
                  {patients.map(patient => (
                    <option key={patient.id} value={patient.id}>
                      {patient.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Drug:</label>
                <select
                  value={formData.drug_id}
                  onChange={(e) => setFormData({...formData, drug_id: e.target.value})}
                  required
                >
                  <option value="">Select Drug</option>
                  {drugs.map(drug => (
                    <option key={drug.id} value={drug.id}>
                      {drug.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Dosage:</label>
                <input
                  type="text"
                  value={formData.dosage}
                  onChange={(e) => setFormData({...formData, dosage: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Frequency:</label>
                <input
                  type="text"
                  value={formData.frequency}
                  onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Duration:</label>
                <input
                  type="text"
                  value={formData.duration}
                  onChange={(e) => setFormData({...formData, duration: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Cost:</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cost_at_time_of_prescription}
                  onChange={(e) => setFormData({...formData, cost_at_time_of_prescription: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Effectiveness:</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.effectiveness_at_time_of_prescription}
                  onChange={(e) => setFormData({...formData, effectiveness_at_time_of_prescription: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>QALY Score:</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.qaly_score}
                  onChange={(e) => setFormData({...formData, qaly_score: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Prescription Date:</label>
                <input
                  type="date"
                  value={formData.prescription_date}
                  onChange={(e) => setFormData({...formData, prescription_date: e.target.value})}
                  required
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingPrescription ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Prescriptions; 