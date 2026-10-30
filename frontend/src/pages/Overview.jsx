import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import CivicMap from '../components/CivicMap';
import {
  Activity,
  AlertTriangle,
  Building2,
  CheckCircle2,
  Clock,
  DollarSign,
  Eye,
  FileText,
  MapPin,
  RefreshCw,
  Repeat,
  ShieldAlert,
  Sparkles,
  Zap,
} from 'lucide-react';

function Overview() {
  const [overview, setOverview] = useState(null);
  const [assets, setAssets] = useState([]);
  const [issues, setIssues] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [triggeringDemo, setTriggeringDemo] = useState(false);
  const [demoNotification, setDemoNotification] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [ovData, assetsData, issuesData, hotspotsData] = await Promise.all([
        civicApi.getOverview(),
        civicApi.getAssets(),
        civicApi.getIssues(),
        civicApi.getHotspots(),
      ]);
      setOverview(ovData);
      setAssets(assetsData);
      setIssues(issuesData);
      setHotspots(hotspotsData);
    } catch (err) {
      setError(err.message || 'Failed to load civic intelligence overview');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTriggerRecurrence = async () => {
    try {
      setTriggeringDemo(true);
      const res = await civicApi.triggerRecurrence();
      setDemoNotification({
        title: '⚡ Recurrence Event Ingested via Dashcam!',
        message: `${res.asset} (${res.asset_code}) detected with recurring pothole. Asset escalated to ${res.risk_level} Risk (${res.new_risk_score}/10).`,
      });
      fetchData();
    } catch (err) {
      alert(`Error triggering recurrence: ${err.message}`);
    } finally {
      setTriggeringDemo(false);
    }
  };

  const handleSeedDemo = async () => {
    try {
      setLoading(true);
      await civicApi.seedDemo();
      setDemoNotification({
        title: '🌱 Demo Scenario Reset & Seeded!',
        message: 'MG Road, Brigade Road, ORR Flyover, Contractors and citizen complaints primed for evaluation.',
      });
      fetchData();
    } catch (err) {
      alert(`Error seeding demo: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* ── Header & Action Controls ── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Civic Infrastructure Intelligence
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              City Memory Active
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Persistent asset lifecycle memory, automated AI failure prediction & duplicate resolution.
          </p>
        </div>

        {/* Demo Scenario Quick-Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleTriggerRecurrence}
            disabled={triggeringDemo}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-red-600/90 text-white hover:bg-red-500 transition shadow-lg shadow-red-600/20"
          >
            <Zap className={`w-3.5 h-3.5 ${triggeringDemo ? 'animate-spin' : ''}`} />
            {triggeringDemo ? 'Simulating Dashcam…' : 'Simulate Recurrence Event'}
          </button>

          <button
            onClick={handleSeedDemo}
            disabled={loading}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition border border-slate-700"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            Reset Demo Dataset
          </button>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 text-slate-400 hover:text-white bg-slate-800/80 rounded-lg border border-slate-700"
            title="Refresh Intelligence Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Demo Interactive Toast / Alert ── */}
      {demoNotification && (
        <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 flex items-start justify-between gap-4 animate-in fade-in slide-in-from-top-2">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-sm font-bold text-red-300">{demoNotification.title}</div>
              <p className="text-xs text-red-200/80 mt-0.5">{demoNotification.message}</p>
            </div>
          </div>
          <button
            onClick={() => setDemoNotification(null)}
            className="text-xs text-red-400 hover:text-red-200"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ── Metric KPI Cards Grid ── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Assets */}
        <div className="card p-4 hover:border-slate-600 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Physical Assets</span>
            <Building2 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {overview?.total_assets ?? '—'}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>100% Tracked in Registry</span>
          </div>
        </div>

        {/* Active Issues */}
        <div className="card p-4 hover:border-slate-600 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Active Defects</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300">
            {overview?.active_issues ?? '—'}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Across {overview?.total_issues ?? 0} total logged
          </div>
        </div>

        {/* Recurring Failures (City Memory USP) */}
        <div className="card p-4 border-red-500/30 bg-red-950/20 hover:border-red-500/50 transition">
          <div className="flex items-center justify-between text-red-300 text-xs font-medium mb-2">
            <span>Recurring Defects</span>
            <Repeat className="w-4 h-4 text-red-400 animate-pulse" />
          </div>
          <div className="text-2xl font-extrabold text-red-400">
            {overview?.recurring_issues ?? '—'}
          </div>
          <div className="text-[11px] text-red-300/80 mt-1">
            {overview?.recurrence_rate_percentage ?? 0}% Failure Repeat Rate
          </div>
        </div>

        {/* AI Observations */}
        <div className="card p-4 hover:border-slate-600 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>AI Observations</span>
            <Eye className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-300">
            {overview?.ai_observations_count ?? '—'}
          </div>
          <div className="text-[11px] text-cyan-400/80 mt-1">
            Dashcam & Civic Vision
          </div>
        </div>

        {/* Total Expenditure */}
        <div className="card p-4 hover:border-slate-600 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Repairs Executed</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            ₹{((overview?.total_civic_expenditure || 0) / 1000).toFixed(0)}k
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {overview?.total_repairs_count || 0} completed work orders
          </div>
        </div>

        {/* Avoidable Repeat Spend */}
        <div className="card p-4 border-amber-500/30 bg-amber-950/20 hover:border-amber-500/50 transition">
          <div className="flex items-center justify-between text-amber-300 text-xs font-medium mb-2">
            <span>Repeat Spend Waste</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-400">
            ₹{((overview?.wasted_repeat_expenditure || 0) / 1000).toFixed(0)}k
          </div>
          <div className="text-[11px] text-amber-300/80 mt-1">
            Preventable via City Memory
          </div>
        </div>
      </div>

      {/* ── Center Stage: Interactive Map & Live Critical Hotspots ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Geospatial Map */}
        <div className="lg:col-span-2 card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">
                City Infrastructure Real-Time Health Map
              </h2>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> Normal Asset
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Critical / Recurring
              </span>
            </div>
          </div>

          <CivicMap
            assets={assets}
            issues={issues}
            hotspots={hotspots}
            height="420px"
          />
        </div>

        {/* High Risk Asset Watchlist */}
        <div className="card p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-red-400" />
                <h3 className="text-sm font-bold text-white">
                  Critical Risk Infrastructure
                </h3>
              </div>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-red-500/20 text-red-400">
                {overview?.critical_risk_assets_count || 0} Priority
              </span>
            </div>

            <div className="space-y-3">
              {assets
                .filter((a) => a.risk_score >= 5.0)
                .slice(0, 4)
                .map((asset) => (
                  <div
                    key={asset.id}
                    className="p-3 rounded-lg bg-slate-900/60 border border-slate-700/60 hover:border-indigo-500/40 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-xs font-semibold text-white">
                          {asset.name}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {asset.asset_code} • {asset.ward}
                        </div>
                      </div>
                      <span className="px-2 py-0.5 text-xs font-bold rounded bg-red-500/20 text-red-400">
                        {asset.risk_score}/10
                      </span>
                    </div>

                    {asset.risk_factors?.length > 0 && (
                      <p className="mt-2 text-[11px] text-red-300/80 bg-red-950/30 px-2 py-1 rounded">
                        ⚠️ {asset.risk_factors[0]}
                      </p>
                    )}
                  </div>
                ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-700/50 text-xs text-slate-400 flex items-center justify-between">
            <span>Average City Health: <b>{overview?.city_average_health || 85}%</b></span>
            <a href="/city-memory" className="text-indigo-400 hover:text-indigo-300 font-medium">
              View Memory Ledger &rarr;
            </a>
          </div>
        </div>
      </div>

      {/* ── The 10-Step Demonstration Walkthrough Banner ── */}
      <div className="card p-6 border-indigo-500/30 bg-gradient-to-r from-indigo-950/30 via-slate-900/80 to-purple-950/30">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h3 className="text-base font-bold text-white">
                Hackathon Primary Demonstration Workflow
              </h3>
            </div>
            <p className="text-xs text-slate-300 mt-1">
              Follow the end-to-end civic lifecycle from citizen grievance to AI duplicate detection, repair, and dashcam recurrence identification.
            </p>
          </div>

          <a
            href="/complaints"
            className="btn-primary text-xs gap-2 whitespace-nowrap"
          >
            Launch Step 1 (Complaints Triage) &rarr;
          </a>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-2">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span className="text-indigo-400 font-bold block mb-1">1. Citizen Report</span>
            Citizen Sanjay files complaint on MG Road pothole. Stored in DB & mapped to physical road asset.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span className="text-indigo-400 font-bold block mb-1">2. Semantic Match</span>
            Citizen Meera reports differently worded crater. AI matches at 84.5% with explainable reason breakdown.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span className="text-indigo-400 font-bold block mb-1">3. Admin Review</span>
            Administrator reviews match criteria, confirms duplicate, and issues Repair Work Order.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span className="text-indigo-400 font-bold block mb-1">4. Dashcam Recurrence</span>
            Vehicle dashcam detects the pothole again post-repair. AI adapter triggers Recurrence Event.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span className="text-indigo-400 font-bold block mb-1">5. Memory Escalation</span>
            City Memory flags warranty breach on Apex InfraWorks and elevates MG Road to High/Critical risk.
          </div>
        </div>
      </div>
    </div>
  );
}

export default Overview;
