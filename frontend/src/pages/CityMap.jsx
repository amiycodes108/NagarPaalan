import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import CivicMap from '../components/CivicMap';
import {
  Building2,
  Filter,
  Layers,
  MapPin,
  RefreshCw,
  Repeat,
  ShieldAlert,
} from 'lucide-react';

function CityMap() {
  const [assets, setAssets] = useState([]);
  const [issues, setIssues] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showCriticalOnly, setShowCriticalOnly] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [aData, iData, hData] = await Promise.all([
        civicApi.getAssets(),
        civicApi.getIssues(),
        civicApi.getHotspots(),
      ]);
      setAssets(aData);
      setIssues(iData);
      setHotspots(hData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredAssets = assets.filter((a) => {
    if (categoryFilter && a.category !== categoryFilter) return false;
    if (showCriticalOnly && a.risk_score < 6.0) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Interactive Geospatial City Map
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              OpenStreetMap + CartoDB
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Spatial monitoring of physical civic infrastructure, defect recurrence density, and AI observation vectors.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700 self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── Map Controls Bar ── */}
      <div className="card p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-slate-300 font-semibold">Filter Category:</span>
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200"
          >
            <option value="">All Categories ({assets.length})</option>
            <option value="Road">Roads</option>
            <option value="Streetlight">Streetlights</option>
            <option value="Drainage">Drainage</option>
            <option value="Waste Point">Waste Points</option>
          </select>

          <label className="flex items-center gap-2 cursor-pointer text-slate-300 ml-2">
            <input
              type="checkbox"
              checked={showCriticalOnly}
              onChange={(e) => setShowCriticalOnly(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-red-500 focus:ring-0"
            />
            <span className="text-red-400 font-semibold">High / Critical Risk Only (&gt;6.0)</span>
          </label>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-blue-500" /> Road
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-yellow-500" /> Streetlight
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-cyan-500" /> Drainage
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500" /> Recurring Defect
          </span>
        </div>
      </div>

      {/* ── Full Interactive Map ── */}
      <CivicMap
        assets={filteredAssets}
        issues={issues}
        hotspots={hotspots}
        selectedAssetId={selectedAsset?.id}
        onSelectAsset={(a) => setSelectedAsset(a)}
        height="640px"
      />

      {/* Asset Quick Detail Modal / Drawer if an asset pin is clicked */}
      {selectedAsset && (
        <div className="card p-4 border border-indigo-500/40 bg-slate-900/90 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-indigo-400">
                {selectedAsset.asset_code}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {selectedAsset.category}
              </span>
              <span className="text-xs text-red-400 font-bold">
                Risk: {selectedAsset.risk_score}/10 ({selectedAsset.risk_level})
              </span>
            </div>
            <h4 className="text-sm font-bold text-white mt-1">
              {selectedAsset.name}
            </h4>
            <p className="text-xs text-slate-400">{selectedAsset.ward} • Health: {selectedAsset.health_score}/100</p>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="/city-memory"
              className="btn-primary text-xs"
            >
              Open City Memory Ledger &rarr;
            </a>
            <button
              onClick={() => setSelectedAsset(null)}
              className="btn-secondary text-xs"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CityMap;
