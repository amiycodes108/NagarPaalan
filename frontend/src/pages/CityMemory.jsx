import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  AlertTriangle,
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  ExternalLink,
  Filter,
  History,
  Layers,
  Repeat,
  Search,
  ShieldAlert,
  Sparkles,
  User,
  Wrench,
  Zap,
} from 'lucide-react';

function CityMemory() {
  const [recurrenceAudit, setRecurrenceAudit] = useState([]);
  const [assets, setAssets] = useState([]);
  const [selectedAssetId, setSelectedAssetId] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEventType, setSelectedEventType] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [auditData, assetsData] = await Promise.all([
        civicApi.getRecurrenceAudit(),
        civicApi.getAssets(),
      ]);
      setRecurrenceAudit(auditData);
      setAssets(assetsData);

      if (assetsData.length > 0) {
        const firstId = assetsData[0].id;
        setSelectedAssetId(firstId);
        const tEvents = await civicApi.getAssetTimeline(firstId);
        setTimeline(tEvents);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectAsset = async (assetId) => {
    try {
      setSelectedAssetId(assetId);
      const tEvents = await civicApi.getAssetTimeline(assetId);
      setTimeline(tEvents);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredTimeline = selectedEventType
    ? timeline.filter((e) => e.event_type === selectedEventType)
    : timeline;

  const currentAsset = assets.find((a) => a.id === selectedAssetId);

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              City Memory™ Central Intelligence Engine
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
              Persistent Asset History
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Searchable historical memory connecting physical assets, defect recurrence cycles, contractor warranty audits, and expenditure.
          </p>
        </div>
      </div>

      {/* ── Section A: City-Wide Chronic Failure & Recurrence Audit ── */}
      <div className="card p-5 space-y-4 border-red-500/30 bg-red-950/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-400 font-extrabold text-base">
            <Repeat className="w-5 h-5 animate-pulse" />
            <span>Chronic Infrastructure Recurrence Audit</span>
          </div>
          <span className="text-xs text-red-300 font-medium">
            {recurrenceAudit.length} Active Chronic Defect Cycles
          </span>
        </div>

        <p className="text-xs text-slate-300">
          The table below demonstrates City Memory's core superpower: detecting when a previously repaired defect reappears on the exact same physical asset, exposing contractor warranty breaches and waste of public capital.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Issue Code</th>
                <th className="py-2.5 px-3">Defect Description</th>
                <th className="py-2.5 px-3">Physical Asset</th>
                <th className="py-2.5 px-3">Recurrence Cycles</th>
                <th className="py-2.5 px-3">Repairs Executed</th>
                <th className="py-2.5 px-3">Repeat Expenditure</th>
                <th className="py-2.5 px-3">Risk Escalation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {recurrenceAudit.map((rec, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-3 font-mono font-bold text-red-400">
                    {rec.issue_code}
                  </td>
                  <td className="py-3 px-3 font-semibold text-white">
                    {rec.title}
                    <div className="text-[11px] text-slate-400 font-normal">
                      {rec.recurrence_notes || 'Defect recurring post-repair'}
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    <span className="font-semibold">{rec.asset_name}</span>
                    <span className="block text-[10px] text-slate-500 font-mono">
                      {rec.asset_code} • {rec.ward}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                      Cycle #{rec.recurrence_count}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-semibold text-white">
                    {rec.repairs_executed} Work Orders
                  </td>
                  <td className="py-3 px-3 font-bold text-amber-400">
                    ₹{(rec.total_repair_cost || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-900/60 text-red-300">
                      {rec.risk_score}/10 ({rec.risk_level})
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Section B: Asset Chronological Timeline Explorer ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Asset Selector List */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Select Infrastructure Asset
            </h2>
          </div>

          <div className="space-y-2">
            {assets.map((asset) => {
              const isSelected = selectedAssetId === asset.id;
              return (
                <div
                  key={asset.id}
                  onClick={() => handleSelectAsset(asset.id)}
                  className={`p-3 rounded-lg cursor-pointer transition border text-xs ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-950/30 shadow-md'
                      : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-indigo-400 font-semibold">
                      {asset.asset_code}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        asset.risk_score >= 6
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      Risk: {asset.risk_score}/10
                    </span>
                  </div>
                  <div className="text-white font-bold mt-1">{asset.name}</div>
                  <div className="text-slate-500 text-[11px]">{asset.ward}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Chronological Timeline Feed */}
        <div className="lg:col-span-2 card p-5 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-indigo-400" />
                <h2 className="text-base font-bold text-white">
                  Chronological City Memory Ledger
                </h2>
              </div>
              {currentAsset && (
                <p className="text-xs text-indigo-300 mt-0.5">
                  Showing historical lifecycle for: <b>{currentAsset.name}</b> ({currentAsset.asset_code})
                </p>
              )}
            </div>

            {/* Filter by Event Type */}
            <select
              value={selectedEventType}
              onChange={(e) => setSelectedEventType(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
            >
              <option value="">All Event Types</option>
              <option value="COMPLAINT_FILED">Complaint Filed</option>
              <option value="AI_OBSERVATION">AI Observation</option>
              <option value="REPAIR_COMPLETED">Repair Completed</option>
              <option value="RECURRENCE_DETECTED">Recurrence Detected</option>
              <option value="WARRANTY_BREACH">Warranty Breach</option>
              <option value="RISK_ESCALATION">Risk Escalation</option>
            </select>
          </div>

          {/* Timeline Events Stack */}
          <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {filteredTimeline.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-xs">
                No events recorded for this filter.
              </div>
            ) : (
              filteredTimeline.map((ev) => {
                const isCritical = ev.severity === 'Critical' || ev.event_type.includes('RECURRENCE') || ev.event_type.includes('WARRANTY');
                const isWarning = ev.severity === 'Warning';

                return (
                  <div key={ev.id} className="relative group text-xs">
                    {/* Timeline Node Dot */}
                    <div
                      className={`absolute -left-[27px] top-1 w-4 h-4 rounded-full border-2 bg-slate-950 ${
                        isCritical
                          ? 'border-red-500 bg-red-500/30 ring-4 ring-red-500/20'
                          : isWarning
                          ? 'border-amber-400 bg-amber-400/20'
                          : 'border-indigo-500 bg-indigo-500/20'
                      }`}
                    />

                    <div
                      className={`p-4 rounded-xl border ${
                        isCritical
                          ? 'border-red-500/40 bg-red-950/20'
                          : 'border-slate-850 bg-slate-900/60'
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                        <span
                          className={`font-mono text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                            isCritical
                              ? 'bg-red-500/20 text-red-300'
                              : 'bg-indigo-500/20 text-indigo-300'
                          }`}
                        >
                          {ev.event_type.replace('_', ' ')}
                        </span>

                        <span className="text-[11px] text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(ev.timestamp).toLocaleString()}
                        </span>
                      </div>

                      <div className="text-sm font-bold text-white mt-1">
                        {ev.summary}
                      </div>

                      <div className="mt-2 text-slate-400 flex items-center gap-3 text-[11px]">
                        <span>Recorded by: <b className="text-slate-300">{ev.actor}</b></span>
                      </div>

                      {ev.details && Object.keys(ev.details).length > 0 && (
                        <div className="mt-2.5 p-2.5 rounded bg-slate-950/80 font-mono text-[11px] text-slate-300 overflow-x-auto border border-slate-800">
                          {JSON.stringify(ev.details, null, 2)}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CityMemory;
