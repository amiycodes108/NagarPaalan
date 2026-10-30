import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  Award,
  CheckCircle2,
  HardHat,
  Plus,
  RefreshCw,
  Repeat,
  ShieldAlert,
  Star,
  Users,
  X,
} from 'lucide-react';

function ContractorManagement() {
  const [contractors, setContractors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    category: 'Road Works',
    contact_person: '',
    email: '',
    phone: '',
    performance_rating: 4.2,
    warranty_adherence_rate: 90.0,
    recurrence_rate: 8.0,
    active_contracts: 2,
  });

  const fetchContractors = async () => {
    try {
      setLoading(true);
      const data = await civicApi.getContractors();
      setContractors(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContractors();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      await civicApi.createContractor(formData);
      setShowNewModal(false);
      fetchContractors();
    } catch (err) {
      alert(`Error creating contractor: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Contractor Accountability & Quality Scoring
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Warranty Auditing Active
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Performance scoring, defect recurrence penalty indexing, and warranty adherence tracking.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowNewModal(true)}
            className="btn-primary text-xs gap-2"
          >
            <Plus className="w-4 h-4" />
            Onboard Contractor
          </button>
          <button
            onClick={fetchContractors}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Contractors Leaderboard ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {contractors.map((c) => {
          const highRecurrence = c.recurrence_rate >= 15.0;

          return (
            <div
              key={c.id}
              className={`card p-5 space-y-4 border transition ${
                highRecurrence
                  ? 'border-red-500/40 bg-red-950/10 hover:border-red-500/60'
                  : 'hover:border-indigo-500/50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-xs font-bold text-indigo-400">
                    {c.contractor_code}
                  </span>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    {c.name}
                  </h3>
                  <span className="text-xs text-slate-400">{c.category}</span>
                </div>

                <div className="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 text-amber-400 font-bold text-xs">
                  <Star className="w-3.5 h-3.5 fill-current" />
                  <span>{c.performance_rating}</span>
                </div>
              </div>

              {/* Quality Indicators */}
              <div className="grid grid-cols-2 gap-3 text-xs bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 text-[10px] uppercase font-semibold">Warranty Adherence</span>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5">
                    {c.warranty_adherence_rate}%
                  </div>
                </div>

                <div>
                  <span className="text-slate-500 text-[10px] uppercase font-semibold">Defect Recurrence</span>
                  <div className={`text-sm font-bold mt-0.5 ${highRecurrence ? 'text-red-400' : 'text-slate-200'}`}>
                    {c.recurrence_rate}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                <span>Active Contracts: <b>{c.active_contracts}</b></span>
                <span>Spend: <b>₹{(c.total_spend || 0).toLocaleString()}</b></span>
              </div>

              {highRecurrence && (
                <div className="p-2 rounded bg-red-950/40 border border-red-500/30 text-[11px] text-red-300 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                  <span>Elevated recurrence penalty flag applied.</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Onboard Contractor Modal ── */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="card p-6 w-full max-w-lg space-y-4 border border-slate-700 bg-slate-900 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">
                Onboard Maintenance Contractor
              </h3>
              <button
                onClick={() => setShowNewModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Company / Entity Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Metro Highway Infrastructure Ltd"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Specialization Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  <option value="Road Works">Road Works & Asphalting</option>
                  <option value="Electrical & Lighting">Electrical & Lighting</option>
                  <option value="Drainage Works">Drainage & Stormwater</option>
                  <option value="Solid Waste">Solid Waste & Sanitation</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Contact Person</label>
                  <input
                    type="text"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Phone</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="btn-primary text-xs"
                >
                  {actionLoading ? 'Saving…' : 'Onboard Contractor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ContractorManagement;
