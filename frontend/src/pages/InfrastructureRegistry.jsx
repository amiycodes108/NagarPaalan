import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Eye,
  Filter,
  Layers,
  MapPin,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  X,
} from 'lucide-react';

function InfrastructureRegistry() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('');
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [showNewModal, setShowNewModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    category: 'Road',
    asset_type: 'Bituminous Arterial Road',
    ward: 'Ward 14 - Central Business District',
    zone: 'Central Zone',
    latitude: 12.9733,
    longitude: 77.6111,
    address: '',
    install_year: 2022,
  });

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (selectedCategory) params.category = selectedCategory;
      if (selectedRisk) params.risk_level = selectedRisk;

      const data = await civicApi.getAssets(params);
      setAssets(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, [search, selectedCategory, selectedRisk]);

  const handleSelectAsset = async (asset) => {
    try {
      const detail = await civicApi.getAsset(asset.id);
      setSelectedAsset(detail);
    } catch (err) {
      setSelectedAsset(asset);
    }
  };

  const handleCreateAsset = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      const created = await civicApi.createAsset(formData);
      setShowNewModal(false);
      fetchAssets();
      handleSelectAsset(created);
    } catch (err) {
      alert(`Asset creation error: ${err.message}`);
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
              Physical Infrastructure Registry
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {assets.length} Assets Registered
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Permanent physical infrastructure identities — road segments, streetlights, stormwater drains, and civic assets.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowNewModal(true)}
            className="btn-primary text-xs gap-2"
          >
            <Plus className="w-4 h-4" />
            Register New Asset
          </button>
          <button
            onClick={fetchAssets}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Search & Filter Controls ── */}
      <div className="card p-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search assets by name, code, or address..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-none text-xs text-white placeholder-slate-500 focus:outline-none w-full"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
          >
            <option value="">All Categories</option>
            <option value="Road">Roads</option>
            <option value="Streetlight">Streetlights</option>
            <option value="Drainage">Drainage</option>
            <option value="Waste Point">Waste Points</option>
          </select>

          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
          >
            <option value="">All Risk Levels</option>
            <option value="Critical">Critical Risk (&gt;7.5)</option>
            <option value="High">High Risk (5-7.5)</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* ── Asset Catalog Grid & Asset Profile Drawer ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Assets List */}
        <div className="lg:col-span-2 space-y-3">
          {assets.map((a) => {
            const isSelected = selectedAsset?.id === a.id;
            const isCritical = a.risk_level === 'Critical' || a.risk_score >= 7.0;

            return (
              <div
                key={a.id}
                onClick={() => handleSelectAsset(a)}
                className={`card p-4 rounded-xl cursor-pointer transition border ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-950/30 shadow-lg shadow-indigo-500/10'
                    : isCritical
                    ? 'border-red-500/40 bg-red-950/10 hover:border-red-500/70'
                    : 'hover:border-slate-600'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-indigo-400">
                        {a.asset_code}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                        {a.category}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        {a.ward}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-white mt-1">
                      {a.name}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">{a.address || 'Address registered'}</p>
                  </div>

                  <div className="text-right flex-shrink-0">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-full text-xs font-bold ${
                        isCritical
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                          : a.risk_score >= 4
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      Risk: {a.risk_score}/10 ({a.risk_level})
                    </span>
                    <div className="text-[11px] text-slate-400 mt-1 font-semibold">
                      Health: {a.health_score}/100
                    </div>
                  </div>
                </div>

                {a.risk_factors?.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-red-300/80 flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                    <span>{a.risk_factors[0]}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Selected Asset City Memory Profile Drawer */}
        <div className="card p-5 space-y-5">
          {!selectedAsset ? (
            <div className="py-24 text-center text-slate-500 text-xs">
              Select any asset on the left to inspect its permanent physical profile, health score, active defects, and chronological City Memory ledger.
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              <div>
                <span className="font-mono text-xs text-indigo-400 font-bold">
                  {selectedAsset.asset_code}
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {selectedAsset.name}
                </h3>
                <p className="text-slate-400 text-xs">{selectedAsset.address}</p>
              </div>

              {/* Health & Risk Meters */}
              <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">
                    Health Index
                  </span>
                  <div className="text-xl font-bold text-emerald-400 mt-0.5">
                    {selectedAsset.health_score}/100
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${selectedAsset.health_score}%` }}
                    />
                  </div>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">
                    Failure Risk Score
                  </span>
                  <div className="text-xl font-bold text-red-400 mt-0.5">
                    {selectedAsset.risk_score}/10
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className="bg-red-500 h-full rounded-full"
                      style={{ width: `${selectedAsset.risk_score * 10}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Explainable Risk Causal Factors */}
              <div>
                <div className="font-bold text-white mb-1.5 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                  <span>Explainable Risk Causal Factors</span>
                </div>
                <div className="space-y-1 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                  {selectedAsset.risk_factors?.length > 0 ? (
                    selectedAsset.risk_factors.map((f, i) => (
                      <div key={i} className="text-red-300 text-[11px] flex items-start gap-1.5">
                        <span>•</span>
                        <span>{f}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-500">No elevated risk factors detected.</span>
                  )}
                </div>
              </div>

              {/* Maintenance Metrics */}
              <div className="grid grid-cols-3 gap-2 text-center p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px]">
                <div>
                  <div className="text-slate-400">Total Defects</div>
                  <div className="font-bold text-white mt-0.5">{selectedAsset.issues_count || 0}</div>
                </div>
                <div>
                  <div className="text-slate-400">Recurring</div>
                  <div className="font-bold text-red-400 mt-0.5">{selectedAsset.recurring_issues_count || 0}</div>
                </div>
                <div>
                  <div className="text-slate-400">Total Repairs</div>
                  <div className="font-bold text-emerald-400 mt-0.5">₹{(selectedAsset.total_repair_cost || 0).toLocaleString()}</div>
                </div>
              </div>

              {/* City Memory Timeline Snippet */}
              <div>
                <div className="font-bold text-white mb-2 flex items-center justify-between">
                  <span>City Memory Ledger ({selectedAsset.memory_events?.length || 0})</span>
                  <a href="/city-memory" className="text-indigo-400 hover:text-indigo-300 text-[11px]">
                    Open Full Timeline &rarr;
                  </a>
                </div>

                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {selectedAsset.memory_events?.slice(0, 4).map((ev) => (
                    <div
                      key={ev.id}
                      className="p-2 rounded bg-slate-900 text-[11px] border-l-2 border-indigo-500"
                    >
                      <div className="text-white font-semibold">{ev.summary}</div>
                      <div className="text-slate-500 text-[10px] mt-0.5">
                        {new Date(ev.timestamp).toLocaleDateString()} by {ev.actor}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── New Asset Modal ── */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="card p-6 w-full max-w-lg space-y-4 border border-slate-700 bg-slate-900 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">
                Register Physical Infrastructure Asset
              </h3>
              <button
                onClick={() => setShowNewModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateAsset} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Asset Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Richmond Road Flyover - South Pier"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  >
                    <option value="Road">Road Segment</option>
                    <option value="Streetlight">Streetlight Corridor</option>
                    <option value="Drainage">Drainage / Canal</option>
                    <option value="Bridge">Bridge / Flyover</option>
                    <option value="Waste Point">Waste Compactor</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Asset Sub-Type</label>
                  <input
                    type="text"
                    value={formData.asset_type}
                    onChange={(e) => setFormData({ ...formData, asset_type: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Ward</label>
                  <input
                    type="text"
                    value={formData.ward}
                    onChange={(e) => setFormData({ ...formData, ward: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Zone</label>
                  <input
                    type="text"
                    value={formData.zone}
                    onChange={(e) => setFormData({ ...formData, zone: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
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
                  {actionLoading ? 'Saving…' : 'Register Asset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default InfrastructureRegistry;
