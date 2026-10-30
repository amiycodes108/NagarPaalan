import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  Calendar,
  CheckCircle2,
  Clock,
  DollarSign,
  FileCheck,
  Plus,
  RefreshCw,
  Repeat,
  ShieldAlert,
  Wrench,
  X,
} from 'lucide-react';

function Maintenance() {
  const [repairs, setRepairs] = useState([]);
  const [assets, setAssets] = useState([]);
  const [contractors, setContractors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const [formData, setFormData] = useState({
    asset_id: 1,
    repair_type: 'Cold Mix Bitumen Asphalt Patch',
    materials: 'VG-30 Bitumen + 12mm Graded Aggregate',
    cost: 35000,
    budget_code: 'CIVIC-CAPEX-WARD14',
    warranty_months: 12,
    contractor_id: 1,
    status: 'Completed',
    notes: 'Emergency road surface patching prior to monsoon season.',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [rData, aData, cData] = await Promise.all([
        civicApi.getRepairs(),
        civicApi.getAssets(),
        civicApi.getContractors(),
      ]);
      setRepairs(rData);
      setAssets(aData);
      setContractors(cData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRepair = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      await civicApi.createRepair(formData);
      setShowNewModal(false);
      fetchData();
    } catch (err) {
      alert(`Error creating repair: ${err.message}`);
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
              Maintenance & Work Order Management
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {repairs.length} Work Orders Logged
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Work order execution, repair cost accounting, warranty tracking, and failure cycle auditing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowNewModal(true)}
            className="btn-primary text-xs gap-2"
          >
            <Plus className="w-4 h-4" />
            Issue Work Order
          </button>
          <button
            onClick={fetchData}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Work Orders Ledger ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Civic Work Orders & Warranty Audit
            </h2>
          </div>
          <span className="text-xs text-slate-400">Total Spend: ₹{repairs.reduce((acc, r) => acc + r.cost, 0).toLocaleString()}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Work Order #</th>
                <th className="py-2.5 px-3">Asset</th>
                <th className="py-2.5 px-3">Repair Type & Materials</th>
                <th className="py-2.5 px-3">Contractor</th>
                <th className="py-2.5 px-3">Cost (₹)</th>
                <th className="py-2.5 px-3">Warranty</th>
                <th className="py-2.5 px-3">Warranty Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {repairs.map((r) => {
                const isBreached = r.recurred_during_warranty;

                return (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-bold text-indigo-400">
                      {r.work_order_no}
                    </td>
                    <td className="py-3 px-3 text-white font-medium">
                      {r.asset_name || `Asset #${r.asset_id}`}
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-semibold text-white">{r.repair_type}</div>
                      <div className="text-[11px] text-slate-400">{r.materials || 'Standard Specs'}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-300 font-medium">
                      {r.contractor_name || 'Apex InfraWorks'}
                    </td>
                    <td className="py-3 px-3 font-bold text-white">
                      ₹{r.cost.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {r.warranty_months} Months
                    </td>
                    <td className="py-3 px-3">
                      {isBreached ? (
                        <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1 w-max">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          Warranty Breached!
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-max">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Warranty Intact
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Issue Work Order Modal ── */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="card p-6 w-full max-w-lg space-y-4 border border-slate-700 bg-slate-900 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">
                Issue Civic Maintenance Work Order
              </h3>
              <button
                onClick={() => setShowNewModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRepair} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Target Physical Asset</label>
                <select
                  value={formData.asset_id}
                  onChange={(e) => setFormData({ ...formData, asset_id: parseInt(e.target.value) })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  {assets.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.asset_code} — {a.name} ({a.ward})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Contractor</label>
                <select
                  value={formData.contractor_id}
                  onChange={(e) => setFormData({ ...formData, contractor_id: parseInt(e.target.value) })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  {contractors.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Repair Execution Type</label>
                <input
                  type="text"
                  required
                  value={formData.repair_type}
                  onChange={(e) => setFormData({ ...formData, repair_type: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Cost (₹)</label>
                  <input
                    type="number"
                    required
                    value={formData.cost}
                    onChange={(e) => setFormData({ ...formData, cost: parseFloat(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Warranty (Months)</label>
                  <input
                    type="number"
                    value={formData.warranty_months}
                    onChange={(e) => setFormData({ ...formData, warranty_months: parseInt(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Materials Specification</label>
                <input
                  type="text"
                  value={formData.materials}
                  onChange={(e) => setFormData({ ...formData, materials: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                />
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
                  {actionLoading ? 'Issuing Order…' : 'Issue Work Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Maintenance;
