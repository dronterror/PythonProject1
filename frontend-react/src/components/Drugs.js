import React, { useState, useEffect } from 'react';
import { drugsAPI } from '../services/api';
import './Drugs.css';

const Drugs = () => {
  const [drugs, setDrugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingDrug, setEditingDrug] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    manufacturer: '',
    price_per_unit: '',
    description: '',
    active_ingredient: '',
    dosage_form: '',
    strength: ''
  });

  useEffect(() => {
    fetchDrugs();
  }, []);

  const fetchDrugs = async () => {
    try {
      setLoading(true);
      const response = await drugsAPI.getAll();
      // Ensure we always set an array, even if the API returns something unexpected
      const drugsData = Array.isArray(response.data) ? response.data : [];
      setDrugs(drugsData);
      setError(null);
    } catch (err) {
      setError('Failed to fetch drugs');
      console.error('Error fetching drugs:', err);
      setDrugs([]); // Ensure we always have an array
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingDrug) {
        await drugsAPI.update(editingDrug.id, formData);
      } else {
        await drugsAPI.create(formData);
      }
      setShowModal(false);
      setEditingDrug(null);
      resetForm();
      fetchDrugs();
    } catch (err) {
      setError('Failed to save drug');
      console.error('Error saving drug:', err);
    }
  };

  const handleEdit = (drug) => {
    setEditingDrug(drug);
    setFormData({
      name: drug.name,
      manufacturer: drug.manufacturer,
      price_per_unit: drug.price_per_unit,
      description: drug.description,
      active_ingredient: drug.active_ingredient,
      dosage_form: drug.dosage_form,
      strength: drug.strength
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this drug?')) {
      try {
        await drugsAPI.delete(id);
        fetchDrugs();
      } catch (err) {
        setError('Failed to delete drug');
        console.error('Error deleting drug:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      manufacturer: '',
      price_per_unit: '',
      description: '',
      active_ingredient: '',
      dosage_form: '',
      strength: ''
    });
  };

  const openModal = () => {
    setShowModal(true);
    setEditingDrug(null);
    resetForm();
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingDrug(null);
    resetForm();
  };

  if (loading) return <div className="loading">Loading drugs...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="drugs-container">
      <div className="header">
        <h2>Drug Management</h2>
        <button className="btn-primary" onClick={openModal}>
          Add New Drug
        </button>
      </div>

      <div className="drugs-grid">
        {Array.isArray(drugs) && drugs.map((drug) => (
          <div key={drug.id} className="drug-card">
            <div className="drug-header">
              <h3>{drug.name}</h3>
              <div className="drug-actions">
                <button 
                  className="btn-edit" 
                  onClick={() => handleEdit(drug)}
                >
                  Edit
                </button>
                <button 
                  className="btn-delete" 
                  onClick={() => handleDelete(drug.id)}
                >
                  Delete
                </button>
              </div>
            </div>
            <div className="drug-details">
              <p><strong>Manufacturer:</strong> {drug.manufacturer}</p>
              <p><strong>Price:</strong> ${drug.price_per_unit}</p>
              <p><strong>Active Ingredient:</strong> {drug.active_ingredient}</p>
              <p><strong>Dosage Form:</strong> {drug.dosage_form}</p>
              <p><strong>Strength:</strong> {drug.strength}</p>
              {drug.description && (
                <p><strong>Description:</strong> {drug.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{editingDrug ? 'Edit Drug' : 'Add New Drug'}</h3>
              <button className="close-btn" onClick={closeModal}>×</button>
            </div>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label>Name:</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Manufacturer:</label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Price per Unit:</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price_per_unit}
                  onChange={(e) => setFormData({...formData, price_per_unit: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Active Ingredient:</label>
                <input
                  type="text"
                  value={formData.active_ingredient}
                  onChange={(e) => setFormData({...formData, active_ingredient: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Dosage Form:</label>
                <input
                  type="text"
                  value={formData.dosage_form}
                  onChange={(e) => setFormData({...formData, dosage_form: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Strength:</label>
                <input
                  type="text"
                  value={formData.strength}
                  onChange={(e) => setFormData({...formData, strength: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows="3"
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingDrug ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Drugs; 