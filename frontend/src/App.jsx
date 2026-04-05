import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000/ws/notifications';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [notifications, setNotifications] = useState([]);

  // WebSocket Connection for Real-Time Alerts
  useEffect(() => {
    const ws = new WebSocket(WS_BASE);
    ws.onmessage = (event) => {
      setNotifications(prev => [event.data, ...prev]);
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        setNotifications(prev => prev.slice(0, prev.length - 1));
      }, 5000);
    };
    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen font-sans text-gray-800">
      {/* Navigation Bar */}
      <nav className="bg-blue-900 text-white p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-bold">Advanced AI Ticketing</h1>
        <div className="space-x-4">
          <button onClick={() => setActiveTab('dashboard')} className={`hover:text-blue-300 ${activeTab === 'dashboard' && 'underline font-semibold'}`}>Dashboard</button>
          <button onClick={() => setActiveTab('submit')} className={`hover:text-blue-300 ${activeTab === 'submit' && 'underline font-semibold'}`}>Submit Ticket</button>
          <button onClick={() => setActiveTab('employees')} className={`hover:text-blue-300 ${activeTab === 'employees' && 'underline font-semibold'}`}>Directory</button>
        </div>
      </nav>

      {/* Floating Notifications */}
      <div className="fixed top-16 right-4 z-50 space-y-2">
        {notifications.map((note, idx) => (
          <div key={idx} className="bg-green-500 text-white px-4 py-2 rounded shadow-lg animate-bounce">
            🔔 {note}
          </div>
        ))}
      </div>

      {/* Main Content Area */}
      <main className="p-8 max-w-6xl mx-auto">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'submit' && <TicketIntake />}
        {activeTab === 'employees' && <EmployeeDirectory />}
      </main>
    </div>
  );
}

// --- COMPONENT: Dashboard (Module 6) ---
function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/analytics`)
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return <div className="text-center mt-10 animate-pulse">Loading Analytics...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">System Analytics</h2>
      
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded shadow border-t-4 border-blue-500">
          <h3 className="text-gray-500 text-sm uppercase">Open Tickets</h3>
          <p className="text-3xl font-bold">{data.metrics.total_open}</p>
        </div>
        <div className="bg-white p-6 rounded shadow border-t-4 border-green-500">
          <h3 className="text-gray-500 text-sm uppercase">Resolved</h3>
          <p className="text-3xl font-bold">{data.metrics.total_resolved}</p>
        </div>
        <div className="bg-white p-6 rounded shadow border-t-4 border-purple-500">
          <h3 className="text-gray-500 text-sm uppercase">Auto-Resolved by AI</h3>
          <p className="text-3xl font-bold">{data.metrics.total_autoresolved}</p>
        </div>
      </div>

      {/* Department Load */}
      <div className="bg-white p-6 rounded shadow">
        <h3 className="text-lg font-bold mb-4">Current Load by Department</h3>
        <div className="flex space-x-4">
          {Object.entries(data.department_load || {}).map(([dept, count]) => (
            <div key={dept} className="bg-gray-100 p-4 rounded text-center min-w-[120px]">
              <div className="text-xl font-bold">{count}</div>
              <div className="text-sm text-gray-600">{dept}</div>
            </div>
          ))}
          {Object.keys(data.department_load || {}).length === 0 && <p className="text-gray-500">No active tickets.</p>}
        </div>
      </div>
    </div>
  );
}

// --- COMPONENT: Ticket Intake (Module 1, 2, 3) ---
function TicketIntake() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/tickets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      setResult(data);
      setText('');
    } catch (error) {
      console.error(error);
      alert("Failed to submit ticket.");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-2xl font-bold mb-4">Submit a Ticket</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea 
            className="w-full border p-3 rounded focus:ring-2 focus:ring-blue-500 outline-none"
            rows="4" 
            placeholder="Describe your issue in detail..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
          />
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'AI is Analyzing...' : 'Submit to AI'}
          </button>
        </form>
      </div>

      {/* AI Results View */}
      {result && (
        <div className={`p-6 rounded shadow border-l-4 ${result.resolution_type === 'Auto-resolve' ? 'bg-green-50 border-green-500' : 'bg-yellow-50 border-yellow-500'}`}>
          <h3 className="text-xl font-bold mb-2">AI Analysis Complete</h3>
          <div className="grid grid-cols-2 gap-2 text-sm mb-4">
            <p><strong>Category:</strong> {result.category}</p>
            <p><strong>Severity:</strong> <span className={`px-2 py-1 rounded text-white ${result.severity === 'Critical' ? 'bg-red-600' : 'bg-gray-500'}`}>{result.severity}</span></p>
            <p><strong>Sentiment:</strong> {result.sentiment}</p>
            <p><strong>Confidence:</strong> {result.confidence_score}%</p>
            <p><strong>Action:</strong> {result.resolution_type}</p>
            <p><strong>Department:</strong> {result.department}</p>
          </div>
          
          <div className="bg-white p-4 rounded border">
            <p className="text-gray-700"><strong>AI Summary:</strong> {result.summary}</p>
          </div>

          {result.resolution_type === 'Auto-resolve' && (
            <div className="mt-4 bg-white p-4 rounded border border-green-200">
              <h4 className="font-bold text-green-700 mb-2">Auto-Response:</h4>
              <p className="text-gray-700">{result.auto_response}</p>
            </div>
          )}

          {result.resolution_type === 'Assign' && (
            <div className="mt-4 bg-white p-4 rounded border border-yellow-200">
              <h4 className="font-bold text-yellow-700 mb-2">Routing Decision:</h4>
              <p className="text-gray-700">
                Routed to <strong>{result.department}</strong>. 
                {result.assigned_employee_id ? ` Assigned to Employee ID: ${result.assigned_employee_id}.` : ' Pending manual assignment.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// --- COMPONENT: Employee Directory (Module 4) ---
function EmployeeDirectory() {
  const [employees, setEmployees] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const fetchEmployees = () => {
    fetch(`${API_BASE}/employees`)
      .then(res => res.json())
      .then(setEmployees)
      .catch(console.error);
  };

  useEffect(() => fetchEmployees(), []);

  const handleAdd = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    await fetch(`${API_BASE}/employees`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    setShowForm(false);
    fetchEmployees();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Employee Directory</h2>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ Add Employee'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAdd} className="bg-white p-6 rounded shadow grid grid-cols-2 gap-4">
          <input name="name" placeholder="Full Name" required className="border p-2 rounded" />
          <input name="email" type="email" placeholder="Email" required className="border p-2 rounded" />
          <select name="department" className="border p-2 rounded">
            <option>IT</option><option>HR</option><option>Engineering</option><option>Finance</option>
          </select>
          <input name="role" placeholder="Role (e.g., Support Tech)" required className="border p-2 rounded" />
          <input name="skills" placeholder="Skills (comma separated)" required className="border p-2 rounded col-span-2" />
          <button type="submit" className="bg-green-600 text-white py-2 rounded col-span-2 hover:bg-green-700">Save Employee</button>
        </form>
      )}

      <div className="bg-white shadow rounded overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th className="p-3">Name</th>
              <th className="p-3">Department</th>
              <th className="p-3">Skills</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-center">Active Load</th>
            </tr>
          </thead>
          <tbody>
            {employees.map(emp => (
              <tr key={emp.id} className="border-b hover:bg-gray-50">
                <td className="p-3 font-medium">{emp.name}<br/><span className="text-xs text-gray-500">{emp.email}</span></td>
                <td className="p-3">{emp.department}</td>
                <td className="p-3 text-sm">{emp.skills}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs text-white ${emp.availability === 'Available' ? 'bg-green-500' : 'bg-red-500'}`}>
                    {emp.availability}
                  </span>
                </td>
                <td className="p-3 text-center font-bold">{emp.current_ticket_load}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {employees.length === 0 && <p className="p-6 text-center text-gray-500">No employees found. Add one to start routing tickets.</p>}
      </div>
    </div>
  );
}