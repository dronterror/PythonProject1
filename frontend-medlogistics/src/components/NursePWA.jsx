import React, { useState, useEffect } from 'react';
import Modal from './Modal.jsx';

// API Configuration - Updated to use JWT authentication
const API_BASE = '/api';
const NURSE_JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHxlNTNhOTk0ZDNiMzg0ZTQ2ODUzOGNjZjUiLCJlbWFpbCI6Im51cnNlMkB2YWxtZWQuY29tIiwicm9sZSI6Im51cnNlIiwiaWF0IjoxNzUwNzk0NjU0LCJpc3MiOiJodHRwczovL2Rldi1tZWRsb2ctdGVzdC51cy5hdXRoMC5jb20vIiwiYXVkIjoiaHR0cHM6Ly9hcGkubWVkbG9nLmFwcCIsImV4cCI6MTc1MDc5NjQ1NH0.ChnHkvBVzPHabiROfLsh-0jx3Ux2-6meEwbxwCnmFJw';

const NursePWA = () => {
    const [orders, setOrders] = useState([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [isAdminModalOpen, setAdminModalOpen] = useState(false);

    useEffect(() => {
        const fetchOrders = async () => {
            setLoading(true);
            setError(null);
            try {
                // Fetch active orders for MAR using the new collaborative endpoint
                const res = await fetch(`${API_BASE}/orders/active-mar/`, {
                    headers: {
                        'Authorization': `Bearer ${NURSE_JWT_TOKEN}`
                    }
                });
                if (!res.ok) throw new Error('Failed to fetch orders');
                const data = await res.json();
                
                // Map orders to patient-like structure for UI
                const mapped = data.map(order => {
                    // Determine status based on order and administration history
                    let status = 'success';
                    let statusText = 'Completed';
                    let medicationInfo = 'No pending tasks';
                    
                    if (order.status === 'active' && order.administrations.length === 0) {
                        status = 'critical';
                        statusText = 'Overdue';
                        medicationInfo = `${order.drug?.name || 'Unknown'} @ ${order.schedule}`;
                    } else if (order.status === 'active' && order.administrations.length > 0) {
                        status = 'warning';
                        statusText = 'Due Soon';
                        medicationInfo = `${order.drug?.name || 'Unknown'} @ ${order.schedule}`;
                    }
                    
                    return {
                        id: order.id,
                        name: order.patient_name,
                        bed: `Bed ${100 + order.id}`, // Generate bed number based on order ID
                        status,
                        statusText,
                        medicationInfo,
                        order: order
                    };
                });
                setOrders(mapped);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, []);

    const handleAdminister = async () => {
        if (!selectedOrder) return;
        
        try {
            const response = await fetch(`${API_BASE}/administrations/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${NURSE_JWT_TOKEN}`
                },
                body: JSON.stringify({
                    order_id: selectedOrder.id
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to administer medication');
            }
            
            // Refresh orders after successful administration
            const updatedOrders = orders.map(order => 
                order.id === selectedOrder.id 
                    ? { ...order, status: 'success', statusText: 'Completed', medicationInfo: 'No pending tasks' }
                    : order
            );
            setOrders(updatedOrders);
            setAdminModalOpen(false);
            setSelectedOrder(null);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleBackToMenu = () => {
        // Navigate back to the role selection page
        window.location.href = '/';
    };

    const filteredOrders = orders.filter(order =>
        order.name.toLowerCase().includes(search.toLowerCase()) ||
        order.medicationInfo.toLowerCase().includes(search.toLowerCase())
    );

    // CSS styles matching the expected result
    const styles = {
        container: {
            fontFamily: "'Roboto', sans-serif",
            backgroundColor: '#F8F9FA',
            color: '#202124',
            margin: 0,
            fontSize: '14px'
        },
        screen: {
            maxWidth: '420px',
            width: '100%',
            margin: '0 auto',
            backgroundColor: '#FFFFFF'
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            borderBottom: '1px solid #DADCE0'
        },
        title: {
            fontSize: '20px',
            fontWeight: 500
        },
        iconBtn: {
            border: 'none',
            background: 'none',
            padding: '8px',
            cursor: 'pointer',
            color: '#5F6368'
        },
        iconSvg: {
            width: '24px',
            height: '24px'
        },
        backBtn: {
            border: 'none',
            background: 'none',
            padding: '8px',
            cursor: 'pointer',
            color: '#1A73E8',
            fontSize: '14px',
            fontWeight: 500
        },
        toolbar: {
            display: 'flex',
            gap: '8px',
            padding: '12px 16px',
            borderBottom: '1px solid #DADCE0'
        },
        searchBar: {
            flexGrow: 1,
            padding: '8px 12px',
            border: '1px solid #DADCE0',
            borderRadius: '8px',
            fontSize: '14px'
        },
        btn: {
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer'
        },
        btnSecondary: {
            backgroundColor: '#FFFFFF',
            border: '1px solid #DADCE0',
            color: '#1A73E8'
        },
        patientList: {
            listStyle: 'none',
            margin: 0,
            padding: 0
        },
        patientListItem: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px',
            borderBottom: '1px solid #DADCE0',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease'
        },
        patientInfo: {
            flex: 1
        },
        patientName: {
            fontSize: '16px',
            fontWeight: 500,
            marginBottom: '4px'
        },
        patientDetails: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#5F6368'
        },
        statusPill: {
            display: 'inline-block',
            padding: '4px 8px',
            borderRadius: '16px',
            fontSize: '12px',
            fontWeight: 500,
            textTransform: 'uppercase'
        },
        statusPillCritical: {
            backgroundColor: '#FCE8E6',
            color: '#D93025'
        },
        statusPillWarning: {
            backgroundColor: '#FEEFC3',
            color: '#A56500'
        },
        statusPillSuccess: {
            backgroundColor: '#E6F4EA',
            color: '#1E8E3E'
        }
    };

    if (loading) {
        return (
            <div style={styles.container}>
                <div style={styles.screen}>
                    <div style={{ padding: '20px', textAlign: 'center' }}>
                        <div style={{ width: '40px', height: '40px', border: '4px solid #DADCE0', borderTop: '4px solid #1A73E8', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={styles.container}>
                <div style={styles.screen}>
                    <div style={{ padding: '20px', textAlign: 'center', color: '#D93025' }}>
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <div style={styles.screen}>
                <header style={styles.header}>
                    <button style={styles.backBtn} onClick={handleBackToMenu}>
                        ← Menu
                    </button>
                    <div style={styles.title}>Ward 10B</div>
                    <button style={styles.iconBtn}>
                        <svg style={styles.iconSvg} viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"></path>
                        </svg>
                    </button>
                </header>

                <div style={styles.toolbar}>
                    <input
                        type="text"
                        style={styles.searchBar}
                        placeholder="Search patients..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                    <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => alert('Filter clicked!')}>
                        Filter
                    </button>
                </div>

                <ul style={styles.patientList}>
                    {filteredOrders.map((order) => (
                        <li
                            key={order.id}
                            style={{
                                ...styles.patientListItem,
                                backgroundColor: '#FFFFFF'
                            }}
                            onMouseEnter={(e) => e.target.style.backgroundColor = '#F1F3F4'}
                            onMouseLeave={(e) => e.target.style.backgroundColor = '#FFFFFF'}
                            onClick={() => {
                                if (order.status === 'critical' || order.status === 'warning') {
                                    setSelectedOrder(order.order);
                                    setAdminModalOpen(true);
                                }
                            }}
                        >
                            <div style={styles.patientInfo}>
                                <div style={styles.patientName}>{order.name} ({order.bed})</div>
                                <div style={styles.patientDetails}>
                                    <span style={{
                                        ...styles.statusPill,
                                        ...(order.status === 'critical' ? styles.statusPillCritical : 
                                             order.status === 'warning' ? styles.statusPillWarning : 
                                             styles.statusPillSuccess)
                                    }}>
                                        {order.statusText}
                                    </span>
                                    <span>{order.medicationInfo}</span>
                                </div>
                            </div>
                            <div>
                                <svg style={{...styles.iconBtn, color: '#5F6368'}} viewBox="0 0 24 24">
                                    <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"></path>
                                </svg>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
            
            {/* Administer Modal */}
            <Modal isOpen={isAdminModalOpen} onClose={() => setAdminModalOpen(false)} title="Administer Medication">
                {selectedOrder && (
                    <div style={{ padding: '16px' }}>
                        <div style={{ backgroundColor: '#E3F2FD', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                            <h3 style={{ fontWeight: 600, color: '#1565C0', margin: '0 0 8px 0' }}>Patient: {selectedOrder.patient_name}</h3>
                            <p style={{ color: '#1976D2', margin: '4px 0' }}>Medication: {selectedOrder.drug?.name || 'Unknown'}</p>
                            <p style={{ color: '#1976D2', margin: '4px 0' }}>Dosage: {selectedOrder.dosage} units</p>
                            <p style={{ color: '#1976D2', margin: '4px 0' }}>Schedule: {selectedOrder.schedule}</p>
                        </div>
                        
                        <div style={{ backgroundColor: '#FFF3E0', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                            <p style={{ color: '#E65100', fontSize: '14px', margin: 0 }}>
                                <strong>Important:</strong> This will automatically decrement the drug stock by {selectedOrder.dosage} units.
                            </p>
                        </div>
                        
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button 
                                onClick={() => setAdminModalOpen(false)}
                                style={{
                                    flex: 1,
                                    padding: '8px 16px',
                                    borderRadius: '8px',
                                    border: '1px solid #DADCE0',
                                    color: '#5F6368',
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    backgroundColor: '#FFFFFF'
                                }}
                            >
                                Cancel
                            </button>
                            <button 
                                onClick={handleAdminister}
                                style={{
                                    flex: 1,
                                    padding: '8px 16px',
                                    borderRadius: '8px',
                                    backgroundColor: '#1E8E3E',
                                    color: '#FFFFFF',
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    border: 'none'
                                }}
                            >
                                Administer
                            </button>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default NursePWA; 