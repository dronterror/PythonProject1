import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      const [metricsResponse, trendsResponse] = await Promise.all([
        dashboardAPI.getMetrics(),
        dashboardAPI.getTrends()
      ]);
      setMetrics(metricsResponse.data);
      setTrends(trendsResponse.data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
      console.error('Dashboard loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (loading) {
    return <div className="card">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  if (!metrics) {
    return <div className="alert alert-error">No data available</div>;
  }

  return (
    <div>
      <h1>ValMed Dashboard</h1>
      
      <div className="card">
        <h2>Overview</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <h3>Total Patients</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3498db' }}>
              {metrics.overview?.total_patients || 0}
            </p>
          </div>
          <div>
            <h3>Total Drugs</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#e74c3c' }}>
              {metrics.overview?.total_drugs || 0}
            </p>
          </div>
          <div>
            <h3>Total Prescriptions</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2ecc71' }}>
              {metrics.overview?.total_prescriptions || 0}
            </p>
          </div>
          <div>
            <h3>Total Analyses</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f39c12' }}>
              {metrics.overview?.total_analyses || 0}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Financial Metrics</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <h3>Total Revenue</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#27ae60' }}>
              {formatCurrency(metrics.financial?.total_revenue || 0)}
            </p>
          </div>
          <div>
            <h3>Average Prescription Cost</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#8e44ad' }}>
              {formatCurrency(metrics.financial?.average_prescription_cost || 0)}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Effectiveness Metrics</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <h3>Average Effectiveness</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#e67e22' }}>
              {formatPercentage(metrics.effectiveness?.average_effectiveness || 0)}
            </p>
          </div>
          <div>
            <h3>Effective Prescriptions</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#16a085' }}>
              {metrics.effectiveness?.effective_prescriptions_count || 0}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Health Economics</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <h3>Average ICER</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#c0392b' }}>
              {formatCurrency(metrics.health_economics?.average_icer || 0)}
            </p>
          </div>
          <div>
            <h3>Prescriptions with ICER</h3>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2980b9' }}>
              {metrics.health_economics?.prescriptions_with_icer || 0}
            </p>
          </div>
        </div>
      </div>

      {trends && trends.monthly_trends && (
        <div className="card">
          <h2>Monthly Trends</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Prescriptions</th>
                  <th>Revenue</th>
                  <th>Avg Effectiveness</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(trends.monthly_trends) && trends.monthly_trends.map((trend, index) => (
                  <tr key={index}>
                    <td>{trend.month}</td>
                    <td>{trend.prescriptions}</td>
                    <td>{formatCurrency(trend.revenue)}</td>
                    <td>{formatPercentage(trend.avg_effectiveness)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 