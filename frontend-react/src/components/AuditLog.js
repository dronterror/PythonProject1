import React, { useState, useEffect } from 'react';
import { auditLogAPI } from '../services/api';
import './AuditLog.css';

const AuditLog = () => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const response = await auditLogAPI.getAll();
      setAuditLogs(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch audit logs');
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'green';
      case 'update':
        return 'blue';
      case 'delete':
        return 'red';
      case 'login':
        return 'purple';
      case 'logout':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredLogs = auditLogs.filter(log => {
    const matchesFilter = filter === 'all' || log.action.toLowerCase().includes(filter.toLowerCase());
    const matchesSearch = searchTerm === '' || 
      log.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  if (loading) return <div className="loading">Loading audit logs...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="audit-log-container">
      <div className="header">
        <h2>Audit Log</h2>
        <div className="filters">
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Actions</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
          </select>
          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="audit-log-content">
        {filteredLogs.length === 0 ? (
          <div className="no-logs">
            <p>No audit logs found matching your criteria.</p>
          </div>
        ) : (
          <div className="logs-list">
            {filteredLogs.map((log) => (
              <div key={log.id} className="log-item">
                <div className="log-header">
                  <span 
                    className={`action-badge ${getActionColor(log.action)}`}
                  >
                    {log.action}
                  </span>
                  <span className="timestamp">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>
                <div className="log-details">
                  <p><strong>User:</strong> {log.user_email || 'System'}</p>
                  <p><strong>Resource:</strong> {log.resource_type} #{log.resource_id}</p>
                  {log.details && (
                    <p><strong>Details:</strong> {log.details}</p>
                  )}
                  {log.ip_address && (
                    <p><strong>IP Address:</strong> {log.ip_address}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="audit-summary">
        <div className="summary-item">
          <span className="summary-label">Total Logs:</span>
          <span className="summary-value">{auditLogs.length}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Filtered Logs:</span>
          <span className="summary-value">{filteredLogs.length}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Actions Today:</span>
          <span className="summary-value">
            {auditLogs.filter(log => {
              const today = new Date().toDateString();
              return new Date(log.timestamp).toDateString() === today;
            }).length}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AuditLog; 