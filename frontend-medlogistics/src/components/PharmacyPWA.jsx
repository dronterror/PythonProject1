import React, { useState, useEffect } from 'react';

// API Configuration - Updated to use the correct endpoints
const API_BASE = '/api';
const API_KEY = '6029420ddcf35aa43813a21874d7bbd5'; // Pharmacist API key from database

const PharmacyPWA = () => {
    const [loading, setLoading] = useState(true);
    const [medications, setMedications] = useState([]);
    const [activeOrders, setActiveOrders] = useState([]);
    const [search, setSearch] = useState('');
    const [error, setError] = useState(null);

    // Calculate remaining stock after administrations
    const calculateRemainingStock = (drug, orders) => {
        let totalAdministered = 0;
        
        // Sum up all administrations for this drug
        orders.forEach(order => {
            if (order.drug_id === drug.id && order.administrations) {
                totalAdministered += order.administrations.length * order.dosage;
            }
        });
        
        return Math.max(0, drug.current_stock - totalAdministered);
    };

    // Fetch drug inventory and active orders
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            // Fetch drugs inventory
            const drugsRes = await fetch(`${API_BASE}/drugs/`, {
                headers: {
                    'X-API-Key': API_KEY
                }
            });
            if (!drugsRes.ok) throw new Error('Failed to fetch drugs');
            const drugsData = await drugsRes.json();

            // Fetch active orders for MAR calculation
            const ordersRes = await fetch(`${API_BASE}/orders/active-mar/`, {
                headers: {
                    'X-API-Key': API_KEY
                }
            });
            let ordersData = [];
            if (ordersRes.ok) {
                ordersData = await ordersRes.json();
            }
            setActiveOrders(ordersData);
            
            // Map API data to UI structure with stock calculations
            const mapped = drugsData.map(med => {
                const remainingStock = calculateRemainingStock(med, ordersData);
                const totalAdministered = med.current_stock - remainingStock;
                
                let status = 'in-stock', statusText = 'In Stock';
                if (remainingStock === 0) {
                    status = 'out-of-stock'; 
                    statusText = 'Out of Stock';
                } else if (remainingStock <= med.low_stock_threshold) {
                    status = 'low-stock'; 
                    statusText = 'Low Stock';
                }
                
                return {
                    id: med.id,
                    name: `${med.name} ${med.strength} (${med.form})`,
                    status,
                    statusText,
                    originalStock: med.current_stock,
                    remainingStock,
                    totalAdministered,
                    threshold: med.low_stock_threshold,
                    drug: med
                };
            });
            setMedications(mapped);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const updateStock = async (medicationId, newQuantity) => {
        try {
            const response = await fetch(`${API_BASE}/drugs/${medicationId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                body: JSON.stringify({
                    current_stock: newQuantity
                })
            });
            
            if (response.ok) {
                fetchData();
                alert('Stock updated successfully!');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update stock');
            }
        } catch (error) {
            console.error('Error updating stock:', error);
            alert('Error updating stock: ' + error.message);
        }
    };

    const handleBackToMenu = () => {
        // Navigate back to the role selection page
        window.location.href = '/';
    };

    const filteredMeds = medications.filter(m =>
        m.name.toLowerCase().includes(search.toLowerCase())
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
        backBtn: {
            border: 'none',
            background: 'none',
            padding: '8px',
            cursor: 'pointer',
            color: '#1A73E8',
            fontSize: '14px',
            fontWeight: 500
        },
        sectionHeader: {
            padding: '12px 16px',
            backgroundColor: '#F8F9FA',
            borderBottom: '1px solid #DADCE0',
            fontWeight: 600,
            color: '#202124'
        },
        drugList: {
            listStyle: 'none',
            margin: 0,
            padding: 0
        },
        drugListItem: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px',
            borderBottom: '1px solid #DADCE0',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease'
        },
        drugInfo: {
            flex: 1
        },
        drugName: {
            fontSize: '16px',
            fontWeight: 500,
            marginBottom: '4px'
        },
        drugDetails: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#5F6368',
            marginBottom: '4px'
        },
        stockInfo: {
            fontSize: '12px',
            color: '#9AA0A6'
        },
        statusPill: {
            display: 'inline-block',
            padding: '4px 8px',
            borderRadius: '16px',
            fontSize: '12px',
            fontWeight: 500,
            textTransform: 'uppercase'
        },
        statusPillInStock: {
            backgroundColor: '#E3F2FD',
            color: '#1565C0'
        },
        statusPillLowStock: {
            backgroundColor: '#FEEFC3',
            color: '#A56500'
        },
        statusPillOutOfStock: {
            backgroundColor: '#FCE8E6',
            color: '#D93025'
        },
        orderList: {
            listStyle: 'none',
            margin: 0,
            padding: 0
        },
        orderListItem: {
            padding: '12px 16px',
            borderBottom: '1px solid #DADCE0',
            backgroundColor: '#FFFFFF'
        },
        orderInfo: {
            fontSize: '14px',
            fontWeight: 500,
            marginBottom: '4px'
        },
        orderDetails: {
            fontSize: '12px',
            color: '#5F6368',
            marginBottom: '2px'
        },
        orderSchedule: {
            fontSize: '12px',
            color: '#9AA0A6'
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
                    <div style={styles.title}>Drug Inventory & MAR</div>
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
                        placeholder="Search drugs..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                    <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => alert('Filter clicked!')}>
                        Filter
                    </button>
                </div>

                {/* Drug Inventory Section */}
                <div style={styles.sectionHeader}>
                    Drug Inventory ({medications.length} drugs)
                </div>
                <ul style={styles.drugList}>
                    {filteredMeds.map((med) => (
                        <li
                            key={med.id}
                            style={{
                                ...styles.drugListItem,
                                backgroundColor: '#FFFFFF'
                            }}
                            onMouseEnter={(e) => e.target.style.backgroundColor = '#F1F3F4'}
                            onMouseLeave={(e) => e.target.style.backgroundColor = '#FFFFFF'}
                            onClick={() => {
                                const newQuantity = prompt(`Update stock for ${med.name} (current: ${med.originalStock})`, med.originalStock);
                                if (newQuantity !== null && !isNaN(newQuantity)) {
                                    updateStock(med.id, parseInt(newQuantity));
                                }
                            }}
                        >
                            <div style={styles.drugInfo}>
                                <div style={styles.drugName}>{med.name}</div>
                                <div style={styles.drugDetails}>
                                    <span style={{
                                        ...styles.statusPill,
                                        ...(med.status === 'in-stock' ? styles.statusPillInStock : 
                                             med.status === 'low-stock' ? styles.statusPillLowStock : 
                                             styles.statusPillOutOfStock)
                                    }}>
                                        {med.statusText}
                                    </span>
                                    <span>{med.remainingStock} units remaining</span>
                                </div>
                                <div style={styles.stockInfo}>
                                    Original: {med.originalStock} | Administered: {med.totalAdministered} | Threshold: {med.threshold}
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

                {/* Active Orders Section (MAR) */}
                {activeOrders.length > 0 && (
                    <>
                        <div style={styles.sectionHeader}>
                            Active Orders ({activeOrders.length})
                        </div>
                        <ul style={styles.orderList}>
                            {activeOrders.map((order) => (
                                <li key={order.id} style={styles.orderListItem}>
                                    <div style={styles.orderInfo}>{order.patient_name}</div>
                                    <div style={styles.orderDetails}>
                                        {order.drug?.name || 'Unknown drug'} - {order.dosage} units
                                    </div>
                                    <div style={styles.orderSchedule}>{order.schedule}</div>
                                    {order.administrations && order.administrations.length > 0 && (
                                        <div style={{ fontSize: '12px', color: '#1E8E3E', marginTop: '4px' }}>
                                            ✓ Administered {order.administrations.length} time(s)
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </>
                )}
            </div>
        </div>
    );
};

export default PharmacyPWA; 