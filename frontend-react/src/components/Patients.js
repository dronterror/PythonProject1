import React, { useState, useEffect } from 'react';
import { patientsAPI } from '../services/api';

const Patients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({ name: '', date_of_birth: '', gender: '' });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await patientsAPI.getAll();
      setPatients(response.data);
    } catch (err) {
      setError('Failed to load patients');
      console.error('Patients loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await patientsAPI.update(editingId, form);
        setSuccess('Patient updated successfully!');
      } else {
        await patientsAPI.create(form);
        setSuccess('Patient added successfully!');
      }
      setError('');
      resetForm();
      loadPatients();
    } catch (err) {
      setError(editingId ? 'Failed to update patient' : 'Failed to add patient');
      setSuccess('');
    }
  };

  const handleEdit = (patient) => {
    setForm({ name: patient.name, date_of_birth: patient.date_of_birth, gender: patient.gender });
    setEditingId(patient.id);
    setSuccess('');
    setError('');
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this patient?')) {
      return;
    }
    try {
      await patientsAPI.delete(id);
      setSuccess('Patient deleted successfully!');
      setError('');
      loadPatients();
    } catch (err) {
      setError('Failed to delete patient');
      setSuccess('');
    }
  };

  const resetForm = () => {
    setForm({ name: '', date_of_birth: '', gender: '' });
    setEditingId(null);
  };

  if (loading) {
    return <div className="card">Loading patients...</div>;
  }

  return (
    <div>
      <h1>Patients Management</h1>
      
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card">
        <h2>{editingId ? 'Edit Patient' : 'Add New Patient'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Date of Birth:</label>
            <input
              type="date"
              value={form.date_of_birth}
              onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Gender:</label>
            <input
              type="text"
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="btn">
            {editingId ? 'Update Patient' : 'Add Patient'}
          </button>
          {editingId && (
            <button type="button" className="btn" onClick={resetForm}>
              Cancel
            </button>
          )}
        </form>
      </div>

      <div className="card">
        <h2>Patients List</h2>
        {patients.length === 0 ? (
          <p>No patients found.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Date of Birth</th>
                <th>Gender</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr key={patient.id}>
                  <td>{patient.id}</td>
                  <td>{patient.name}</td>
                  <td>{new Date(patient.date_of_birth).toLocaleDateString()}</td>
                  <td>{patient.gender}</td>
                  <td>
                    <button
                      className="btn"
                      onClick={() => handleEdit(patient)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDelete(patient.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Patients; 