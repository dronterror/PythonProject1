import React, { useState, useEffect } from 'react';
import Modal from './Modal.jsx';

const statusPillColors = {
  critical: 'bg-red-100 text-red-600',
  warning: 'bg-yellow-100 text-yellow-700',
  success: 'bg-green-100 text-green-700',
};

// API Configuration - Updated to use the new collaborative endpoint
const API_BASE = '/api';
const API_KEY = '0f83b062004308a71056537a7929aedb'; // Doctor API key from database

const DoctorPWA = () => {
    const [orders, setOrders] = useState([]);
    const [drugs, setDrugs] = useState([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isMenuOpen, setMenuOpen] = useState(false);
    const [isProfileOpen, setProfileOpen] = useState(false);
    const [isOrderOpen, setOrderOpen] = useState(false);
    const [newOrder, setNewOrder] = useState({
        patient_name: '',
        drug_id: '',
        dosage: '',
        schedule: ''
    });

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                // Fetch doctor's own orders using the new collaborative endpoint
                const ordersRes = await fetch(`${API_BASE}/orders/my-orders/`, {
                    headers: {
                        'X-API-Key': API_KEY
                    }
                });
                if (!ordersRes.ok) throw new Error('Failed to fetch orders');
                const ordersData = await ordersRes.json();
                setOrders(ordersData);

                // Fetch drugs
                const drugsRes = await fetch(`${API_BASE}/drugs/`, {
                    headers: {
                        'X-API-Key': API_KEY
                    }
                });
                if (!drugsRes.ok) throw new Error('Failed to fetch drugs');
                const drugsData = await drugsRes.json();
                setDrugs(drugsData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleCreateOrder = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_BASE}/orders/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                body: JSON.stringify(newOrder)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create order');
            }
            
            const createdOrder = await response.json();
            setOrders([...orders, createdOrder]);
            setNewOrder({ patient_name: '', drug_id: '', dosage: '', schedule: '' });
            setOrderOpen(false);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleBackToMenu = () => {
        // Navigate back to the role selection page
        window.location.href = '/';
    };

    const filteredOrders = orders.filter(order =>
        order.patient_name.toLowerCase().includes(search.toLowerCase())
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
        backBtn: {
            border: 'none',
            background: 'none',
            padding: '8px',
            cursor: 'pointer',
            color: '#1A73E8',
            fontSize: '14px',
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
        btnPrimary: {
            backgroundColor: '#1A73E8',
            border: '1px solid #1A73E8',
            color: '#FFFFFF'
        },
        orderList: {
            listStyle: 'none',
            margin: 0,
            padding: 0
        },
        orderListItem: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px',
            borderBottom: '1px solid #DADCE0',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease'
        },
        orderInfo: {
            flex: 1
        },
        orderName: {
            fontSize: '16px',
            fontWeight: 500,
            marginBottom: '4px'
        },
        orderDetails: {
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
        statusPillActive: {
            backgroundColor: '#FEEFC3',
            color: '#A56500'
        },
        statusPillCompleted: {
            backgroundColor: '#E6F4EA',
            color: '#1E8E3E'
        },
        formGroup: {
            marginBottom: '16px'
        },
        label: {
            display: 'block',
            fontWeight: 600,
            marginBottom: '4px',
            color: '#202124'
        },
        input: {
            width: '100%',
            padding: '8px 12px',
            border: '1px solid #DADCE0',
            borderRadius: '8px',
            fontSize: '14px'
        },
        select: {
            width: '100%',
            padding: '8px 12px',
            border: '1px solid #DADCE0',
            borderRadius: '8px',
            fontSize: '14px'
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
                    <div style={styles.title}>My Prescriptions</div>
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
                        placeholder="Search my prescriptions..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                    <button style={{...styles.btn, ...styles.btnPrimary}} onClick={() => setOrderOpen(true)}>
                        New Order
                    </button>
                </div>

                <ul style={styles.orderList}>
                    {filteredOrders.map((order) => (
                        <li
                            key={order.id}
                            style={{
                                ...styles.orderListItem,
                                backgroundColor: '#FFFFFF'
                            }}
                            onMouseEnter={(e) => e.target.style.backgroundColor = '#F1F3F4'}
                            onMouseLeave={(e) => e.target.style.backgroundColor = '#FFFFFF'}
                        >
                            <div style={styles.orderInfo}>
                                <div style={styles.orderName}>{order.patient_name}</div>
                                <div style={styles.orderDetails}>
                                    <span style={{
                                        ...styles.statusPill,
                                        ...(order.status === 'active' ? styles.statusPillActive : styles.statusPillCompleted)
                                    }}>
                                        {order.status}
                                    </span>
                                    <span>{order.drug?.name || 'Unknown drug'} - {order.dosage} units</span>
                                </div>
                                <div style={{ fontSize: '12px', color: '#9AA0A6', marginTop: '4px' }}>{order.schedule}</div>
                                {/* Show administration status if available */}
                                {order.administrations && order.administrations.length > 0 && (
                                    <div style={{ fontSize: '12px', color: '#1E8E3E', marginTop: '4px' }}>
                                        ✓ Administered {order.administrations.length} time(s)
                                    </div>
                                )}
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
            
            {/* New Order Modal */}
            <Modal isOpen={isOrderOpen} onClose={() => setOrderOpen(false)} title="New Order">
                <form style={{ padding: '16px' }} onSubmit={handleCreateOrder}>
                    <div style={styles.formGroup}>
                        <label htmlFor="patient" style={styles.label}>Patient Name</label>
                        <input 
                            id="patient" 
                            style={styles.input}
                            placeholder="Patient name" 
                            value={newOrder.patient_name}
                            onChange={e => setNewOrder({...newOrder, patient_name: e.target.value})}
                            required
                        />
                    </div>
                    <div style={styles.formGroup}>
                        <label htmlFor="medication" style={styles.label}>Medication</label>
                        <select 
                            id="medication" 
                            style={styles.select}
                            value={newOrder.drug_id}
                            onChange={e => setNewOrder({...newOrder, drug_id: parseInt(e.target.value)})}
                            required
                        >
                            <option value="">Select medication</option>
                            {drugs.map(drug => (
                                <option key={drug.id} value={drug.id}>
                                    {drug.name} ({drug.strength}) - Stock: {drug.current_stock}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div style={styles.formGroup}>
                        <label htmlFor="dose" style={styles.label}>Dosage (units)</label>
                        <input 
                            id="dose" 
                            type="number"
                            style={styles.input}
                            placeholder="Dosage" 
                            value={newOrder.dosage}
                            onChange={e => setNewOrder({...newOrder, dosage: parseInt(e.target.value)})}
                            required
                        />
                    </div>
                    <div style={styles.formGroup}>
                        <label htmlFor="instructions" style={styles.label}>Schedule</label>
                        <input 
                            id="instructions" 
                            style={styles.input}
                            placeholder="e.g., Every 8 hours" 
                            value={newOrder.schedule}
                            onChange={e => setNewOrder({...newOrder, schedule: e.target.value})}
                            required
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <button 
                            type="button"
                            onClick={() => setOrderOpen(false)}
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
                            type="submit"
                            style={{
                                flex: 1,
                                padding: '8px 16px',
                                borderRadius: '8px',
                                backgroundColor: '#1A73E8',
                                color: '#FFFFFF',
                                fontWeight: 500,
                                cursor: 'pointer',
                                border: 'none'
                            }}
                        >
                            Create Order
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default DoctorPWA; 