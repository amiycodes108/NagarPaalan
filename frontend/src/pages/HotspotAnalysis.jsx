import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  AlertTriangle,
  Building2,
  Flame,
  Layers,
  MapPin,
  RefreshCw,
  Repeat,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react';

function HotspotAnalysis() {
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHotspots = async () => {
    try {
      setLoading(true);
      const data = await civicApi.getHotspots();
      setHotspots(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHotspots();
  }, []);

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Failure Hotspot & Spatial Risk Analysis
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
              Density Clustering Active
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Geographic concentration of chronic defect recurrences, monsoon vulnerability zones, and predictive risk indices.
          </p>
        </div>

        <button
          onClick={fetchHotspots}
          className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700 self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── Hotspot Summary Cards ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="card p-5 border-red-500/30 bg-red-950/20">
          <div className="flex items-center justify-between text-xs text-red-300 font-bold mb-2">
            <span>Critical Hotspot Clusters</span>
            <Flame className="w-5 h-5 text-red-500" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {hotspots.filter((h) => h.risk_level === 'Critical').length}
          </div>
          <p className="text-[11px] text-red-300/80 mt-1">
            Recurrence index &gt; 7.0/10 requiring immediate capital resurfacing
          </p>
        </div>

        <div className="card p-5 border-amber-500/30 bg-amber-950/20">
          <div className="flex items-center justify-between text-xs text-amber-300 font-bold mb-2">
            <span>High Risk Sectors</span>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {hotspots.filter((h) => h.risk_level === 'High').length}
          </div>
          <p className="text-[11px] text-amber-300/80 mt-1">
            Monsoon waterlogging & heavy transit corridors
          </p>
        </div>

        <div className="card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 font-bold mb-2">
            <span>City Density Radius</span>
            <MapPin className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            350m
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Contiguous cluster threshold for civic work orders
          </p>
        </div>
      </div>

      {/* ── Hotspot Clusters Detailed Ledger ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-red-400" />
            <h2 className="text-base font-bold text-white">
              Identified Spatial Density Clusters
            </h2>
          </div>
          <span className="text-xs text-slate-400">Ranked by Recurrence Velocity</span>
        </div>

        <div className="space-y-4">
          {hotspots.map((h, i) => {
            const isCritical = h.risk_level === 'Critical';

            return (
              <div
                key={i}
                className={`p-4 rounded-xl border transition ${
                  isCritical
                    ? 'border-red-500/40 bg-red-950/20'
                    : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-extrabold text-red-400">
                      {h.cluster_id}
                    </span>
                    <span className="text-sm font-bold text-white">
                      {h.ward}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      ({h.zone})
                    </span>
                  </div>

                  <span
                    className={`self-start sm:self-auto text-xs px-3 py-1 rounded-full font-extrabold ${
                      isCritical
                        ? 'bg-red-500/30 text-red-300 border border-red-500/40'
                        : 'bg-amber-500/20 text-amber-300'
                    }`}
                  >
                    Recurrence Index: {h.recurrence_index}/10 ({h.risk_level})
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-300 mb-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-semibold">Defect Count</span>
                    <div className="font-bold text-white mt-0.5">{h.defect_count} recorded failures</div>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-semibold">Primary Category</span>
                    <div className="font-bold text-white mt-0.5">{h.primary_category}</div>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-semibold">Cluster Radius</span>
                    <div className="font-bold text-white mt-0.5">{h.radius_meters}m</div>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-semibold">Coordinates</span>
                    <div className="font-mono text-indigo-400 mt-0.5">{h.latitude}, {h.longitude}</div>
                  </div>
                </div>

                {/* Top Assets in Hotspot */}
                {h.top_assets?.length > 0 && (
                  <div className="text-[11px] text-slate-400 flex flex-wrap items-center gap-2">
                    <span className="font-semibold text-slate-300">Vulnerable Assets:</span>
                    {h.top_assets.map((assetName, ai) => (
                      <span
                        key={ai}
                        className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700"
                      >
                        {assetName}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default HotspotAnalysis;
