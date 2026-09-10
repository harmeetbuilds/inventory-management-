import React, { useState, useEffect } from 'react';
import { 
  Boxes, 
  Brain, 
  TrendingUp, 
  Truck, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Sliders, 
  Barcode 
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function App() {
  const [productId, setProductId] = useState(1);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);

  // Fetch forecast prediction from FastAPI
  const fetchForecast = async (id = productId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/forecast/recommend/${id}`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error(`Server returned HTTP ${res.status}`);
      const result = await res.json();
      setData(result);
    } catch (err) {
      setError('Failed to connect to FastAPI backend. Ensure Uvicorn is running.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch inventory risk alerts
  const fetchAlerts = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/inventory/alerts');
      if (res.ok) {
        const result = await res.json();
        setAlerts(result);
      }
    } catch (err) {
      console.error('Could not load inventory alerts.');
    }
  };

  useEffect(() => {
    fetchForecast(1);
    fetchAlerts();
  }, []);

  const handleQuickSelect = (id) => {
    setProductId(id);
    fetchForecast(id);
  };

  // Format daily forecast array for Recharts
  const chartData = (data?.daily_forecasts || [12, 19, 15, 22, 30, 26, 21]).map((val, idx) => ({
    day: `Day ${idx + 1}`,
    demand: val
  }));

  const currentStock = data?.current_stock ?? '--';
  const predictedDemand = data?.predicted_demand ?? data?.total_predicted_demand ?? 0;
  const recommendedReorder = data?.recommended_reorder ?? data?.reorder_quantity ?? 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50 px-8 py-3.5 flex justify-between items-center">
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 rounded-xl shadow-lg shadow-indigo-500/20 text-white flex items-center justify-center">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight text-white flex items-center gap-2">
              SmartInventory <span className="text-indigo-400 text-xs px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 font-semibold">REACT AI</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium">Demand Prediction & Risk Analytics</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> FastAPI Online
        </span>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8 flex-1 w-full">
        
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target Product</span>
              <p className="text-2xl font-black text-white mt-1">#{productId}</p>
            </div>
            <div className="p-3 bg-slate-800/60 rounded-xl text-slate-300 border border-slate-700/50">
              <Barcode className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Current Stock</span>
              <p className="text-2xl font-black text-slate-200 mt-1">{currentStock}</p>
            </div>
            <div className="p-3 bg-slate-800/60 rounded-xl text-slate-300 border border-slate-700/50">
              <Boxes className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">7-Day Demand</span>
              <p className="text-2xl font-black text-indigo-400 mt-1">{predictedDemand}</p>
            </div>
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Suggested Reorder</span>
              <p className="text-2xl font-black text-cyan-400 mt-1">{recommendedReorder}</p>
            </div>
            <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
              <Truck className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Dashboard Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Controls */}
          <div className="space-y-6">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-indigo-400" /> Forecast Parameters
              </h2>
              
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-400 uppercase">Product ID</label>
                <input 
                  type="number" 
                  value={productId} 
                  onChange={(e) => setProductId(Number(e.target.value))}
                  min="1"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                />
              </div>

              <div>
                <span className="block text-xs font-medium text-slate-500 mb-2">Quick Select Sample:</span>
                <div className="flex gap-2">
                  {[1, 2, 3].map((id) => (
                    <button 
                      key={id}
                      onClick={() => handleQuickSelect(id)}
                      className="flex-1 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium rounded-lg border border-slate-700 transition"
                    >
                      ID #{id}
                    </button>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => fetchForecast()} 
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 active:scale-[0.98] text-white py-3.5 rounded-xl font-bold transition duration-200 flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 text-sm"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                Run ML Prediction
              </button>

              {error && (
                <div className="p-4 rounded-xl text-xs bg-red-500/10 border border-red-500/30 text-red-400 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
                </div>
              )}

              {data && !error && (
                <div className={`p-4 rounded-xl text-xs font-medium border flex items-center gap-3 ${
                  data.alert_severity === 'CRITICAL' || currentStock < predictedDemand
                    ? 'bg-red-500/10 border-red-500/30 text-red-400'
                    : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                }`}>
                  {data.alert_severity === 'CRITICAL' || currentStock < predictedDemand ? (
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 shrink-0" />
                  )}
                  <div>
                    <strong>{currentStock < predictedDemand ? 'Stock Alert:' : 'Healthy Stock:'}</strong>{' '}
                    {currentStock < predictedDemand ? 'Stock is below forecasted demand. Reorder suggested.' : 'Inventory levels look optimal.'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recharts Analytics */}
          <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-400" /> ML Predicted Demand Trajectory
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">7-Day aggregate consumption trends estimated by ML model</p>
              </div>
            </div>

            <div className="w-full h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    itemStyle={{ color: '#818cf8' }}
                  />
                  <Area type="monotone" dataKey="demand" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorDemand)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

        {/* Alerts Table */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-cyan-400" /> Active System Inventory Warnings
              </h3>
              <p className="text-xs text-slate-400">Automated warning logs triggered by stock threshold calculations</p>
            </div>
            <button onClick={fetchAlerts} className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 bg-indigo-500/10 px-3 py-1.5 rounded-lg border border-indigo-500/20 transition">
              <RefreshCw className="w-3.5 h-3.5" /> Refresh Alerts
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Product ID</th>
                  <th className="py-3 px-4">Current Stock</th>
                  <th className="py-3 px-4">Safety Stock</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {alerts.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="py-4 text-center text-slate-500">No active inventory alerts found.</td>
                  </tr>
                ) : (
                  alerts.map((a, i) => (
                    <tr key={i} className="hover:bg-slate-900/40 transition">
                      <td className="py-3 px-4 text-white font-bold">#{a.product_id}</td>
                      <td className="py-3 px-4 text-slate-300">{a.current_stock} units</td>
                      <td className="py-3 px-4 text-slate-400">{a.safety_stock ?? 'N/A'}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                          a.alert_severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {a.alert_severity || 'WARNING'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{a.message || 'Action Required'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}
