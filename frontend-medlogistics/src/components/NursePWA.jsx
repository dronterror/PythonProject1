import React, { useState, useEffect } from 'react';

const statusPillColors = {
  critical: 'bg-red-100 text-red-600',
  warning: 'bg-yellow-100 text-yellow-700',
  success: 'bg-green-100 text-green-700',
};

const NursePWA = () => {
    const [patients, setPatients] = useState([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPatients = async () => {
            setLoading(true);
            setError(null);
            try {
                const res = await fetch('/medication/ward/patients');
                if (!res.ok) throw new Error('Failed to fetch patients');
                const data = await res.json();
                // Map API data to UI structure
                const mapped = data.map(p => {
                    let status = 'success', statusText = 'Completed', med = '', time = '';
                    if (p.overdue_count > 0) {
                        status = 'critical'; statusText = 'Overdue';
                        med = p.overdue_medication_name || '';
                        time = p.overdue_time || '';
                    } else if (p.due_count > 0) {
                        status = 'warning'; statusText = 'Due Soon';
                        med = p.due_medication_name || '';
                        time = p.due_time || '';
                    }
                    return {
                        id: p.id,
                        name: p.name,
                        bed: p.bed_number,
                        status,
                        statusText,
                        med,
                        time,
                    };
                });
                setPatients(mapped);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchPatients();
    }, []);

    const filteredPatients = patients.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        (p.bed && p.bed.includes(search))
    );

    return (
        <div className="max-w-md w-full mx-auto my-8 bg-white shadow rounded-lg animate-fade-in">
            <header className="flex justify-between items-center px-4 py-3 border-b border-gray-200">
                <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none" aria-label="Menu" onClick={() => alert('Menu clicked!')}>
                    <svg viewBox="0 0 24 24" className="w-6 h-6"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path></svg>
                </button>
                <div className="text-lg font-semibold">Ward 10B</div>
                <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none" aria-label="Profile" onClick={() => alert('Profile clicked!')}>
                    <svg viewBox="0 0 24 24" className="w-6 h-6"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"></path></svg>
                </button>
            </header>
            <div className="flex gap-2 px-4 py-3 border-b border-gray-200">
                <input
                    type="text"
                    className="flex-grow px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-200 text-sm"
                    placeholder="Search patients..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <button className="px-4 py-2 rounded border border-blue-500 text-blue-600 font-medium hover:bg-blue-50 transition" onClick={() => alert('Filter clicked!')}>Filter</button>
            </div>
            {loading ? (
                <div className="py-12 text-center">
                  <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mx-auto" aria-label="Loading"></div>
                </div>
            ) : error ? (
                <div className="py-8 text-center text-red-600">{error}</div>
            ) : (
                <ul className="divide-y divide-gray-100">
                    {filteredPatients.map((patient, idx) => (
                        <li
                          className="flex justify-between items-center px-4 py-4 cursor-pointer bg-white hover:bg-blue-50 transition-all duration-200 opacity-0 translate-y-4 animate-list-fade-in"
                          key={patient.id}
                          style={{ animationDelay: `${idx * 60}ms` }}
                        >
                            <div className="flex-1">
                                <div className="font-medium text-base mb-1">{patient.name} (Bed {patient.bed})</div>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold uppercase ${statusPillColors[patient.status]}`}>{patient.statusText}</span>
                                    {patient.status !== 'success' ? (
                                        <span>{patient.med} @ {patient.time}</span>
                                    ) : (
                                        <span>No pending tasks</span>
                                    )}
                                </div>
                            </div>
                            <div className="ml-2">
                                <svg className="w-6 h-6 text-gray-400" viewBox="0 0 24 24"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"></path></svg>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default NursePWA; 