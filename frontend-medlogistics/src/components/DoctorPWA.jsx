import React, { useState, useEffect } from 'react';
import Modal from './Modal.jsx';

const statusPillColors = {
  critical: 'bg-red-100 text-red-600',
  warning: 'bg-yellow-100 text-yellow-700',
  success: 'bg-green-100 text-green-700',
};

// API Configuration
const API_BASE = '/api';
const API_KEY = '0f83b062004308a71056537a7929aedb'; // Doctor API key

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
                // Fetch orders
                const ordersRes = await fetch(`${API_BASE}/orders/`, {
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

    const filteredOrders = orders.filter(order =>
        order.patient_name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="max-w-md w-full mx-auto my-8 bg-white shadow rounded-lg animate-fade-in">
            <header className="flex justify-between items-center px-4 py-3 border-b border-gray-200">
                <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none" aria-label="Menu" onClick={() => setMenuOpen(true)}>
                    <svg viewBox="0 0 24 24" className="w-6 h-6"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path></svg>
                </button>
                <div className="text-lg font-semibold">Doctor Orders</div>
                <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none" aria-label="Profile" onClick={() => setProfileOpen(true)}>
                    <svg viewBox="0 0 24 24" className="w-6 h-6"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"></path></svg>
                </button>
            </header>
            <div className="flex gap-2 px-4 py-3 border-b border-gray-200">
                <input
                    type="text"
                    className="flex-grow px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200 text-sm"
                    placeholder="Search orders..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <button className="px-4 py-2 rounded border border-blue-500 text-blue-600 font-medium hover:bg-blue-50 transition" onClick={() => setOrderOpen(true)}>New Order</button>
            </div>
            {loading ? (
                <div className="py-12 text-center">
                  <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mx-auto" aria-label="Loading"></div>
                </div>
            ) : error ? (
                <div className="py-8 text-center text-red-600">{error}</div>
            ) : (
                <ul className="divide-y divide-gray-100">
                    {filteredOrders.map((order, idx) => (
                        <li
                          className="flex justify-between items-center px-4 py-4 cursor-pointer bg-white hover:bg-blue-50 transition-all duration-200 opacity-0 translate-y-4 animate-list-fade-in"
                          key={order.id}
                          style={{ animationDelay: `${idx * 60}ms` }}
                        >
                            <div className="flex-1">
                                <div className="font-medium text-base mb-1">{order.patient_name}</div>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold uppercase ${statusPillColors[order.status === 'active' ? 'warning' : 'success']}`}>
                                        {order.status}
                                    </span>
                                    <span>{order.drug?.name || 'Unknown drug'} - {order.dosage} units</span>
                                </div>
                                <div className="text-xs text-gray-400 mt-1">{order.schedule}</div>
                            </div>
                            <div className="ml-2">
                                <svg className="w-6 h-6 text-gray-400" viewBox="0 0 24 24"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"></path></svg>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
            <Modal isOpen={isMenuOpen} onClose={() => setMenuOpen(false)} title="Menu">
              <p>Menu content goes here.</p>
            </Modal>
            <Modal isOpen={isProfileOpen} onClose={() => setProfileOpen(false)} title="Profile">
              <p>Profile content goes here.</p>
            </Modal>
            <Modal isOpen={isOrderOpen} onClose={() => setOrderOpen(false)} title="New Order">
              <form className="space-y-4" onSubmit={handleCreateOrder}>
                <div>
                  <label htmlFor="patient" className="block font-semibold mb-1">Patient Name</label>
                  <input 
                    id="patient" 
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200" 
                    placeholder="Patient name" 
                    value={newOrder.patient_name}
                    onChange={e => setNewOrder({...newOrder, patient_name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="medication" className="block font-semibold mb-1">Medication</label>
                  <select 
                    id="medication" 
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200"
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
                <div>
                  <label htmlFor="dose" className="block font-semibold mb-1">Dosage (units)</label>
                  <input 
                    id="dose" 
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200" 
                    placeholder="Dosage" 
                    value={newOrder.dosage}
                    onChange={e => setNewOrder({...newOrder, dosage: parseInt(e.target.value)})}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="instructions" className="block font-semibold mb-1">Schedule</label>
                  <input 
                    id="instructions" 
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200" 
                    placeholder="e.g., every 6 hours" 
                    value={newOrder.schedule}
                    onChange={e => setNewOrder({...newOrder, schedule: e.target.value})}
                    required
                  />
                </div>
                <button type="submit" className="w-full py-2 px-4 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700 transition">Submit Order</button>
              </form>
            </Modal>
        </div>
    );
};

export default DoctorPWA; 