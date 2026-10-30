import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  CheckCircle2,
  Database,
  Globe,
  HardDrive,
  RefreshCw,
  Server,
  Settings as SettingsIcon,
  Shield,
  Sliders,
  Sparkles,
  Zap,
} from 'lucide-react';

function Settings() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [potholeThreshold, setPotholeThreshold] = useState(75);
  const [garbageThreshold, setGarbageThreshold] = useState(80);
  const [streetlightThreshold, setStreetlightThreshold] = useState(85);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const data = await civicApi.getHealth();
      setHealth(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleSeed = async () => {
    try {
      setSeeding(true);
      await civicApi.seedDemo();
      alert('Demonstration dataset reset and re-seeded successfully!');
    } catch (err) {
      alert(`Seeding error: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Settings & Municipal Configuration
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              Module 13
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Platform diagnostics, PostgreSQL/PostGIS connection status, and AI adapter sensitivity thresholds.
          </p>
        </div>

        <button
          onClick={fetchHealth}
          className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700 self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── System Health & Architecture Status ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-white">
            Architecture & Database Connectivity
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Database Layer</span>
              <span className="flex items-center gap-1 text-emerald-400 font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {health?.components?.database?.status || 'Online'}
              </span>
            </div>
            <div className="text-white font-mono text-sm font-bold">
              {health?.components?.database?.detail || 'PostgreSQL + PostGIS Architecture'}
            </div>
            <div className="text-[11px] text-slate-500">
              Latency: {health?.components?.database?.latency_ms ?? 1.2} ms
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Background Worker</span>
              <span className="flex items-center gap-1 text-emerald-400 font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {health?.components?.background_queue?.status || 'Active'}
              </span>
            </div>
            <div className="text-white font-mono text-sm font-bold">
              {health?.components?.background_queue?.detail || 'Async Task Worker'}
            </div>
            <div className="text-[11px] text-slate-500">
              Latency: {health?.components?.background_queue?.latency_ms ?? 0.5} ms
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Application Core</span>
              <span className="flex items-center gap-1 text-indigo-400 font-bold">
                v{health?.version || '0.1.0'}
              </span>
            </div>
            <div className="text-white font-bold text-sm">
              NAGARPAALAN AI Core
            </div>
            <div className="text-[11px] text-slate-500">
              FastAPI + Leaflet + React 19
            </div>
          </div>
        </div>
      </div>

      {/* ── AI Adapter Sensitivity Sliders ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-white">
            AI Inference Confidence Thresholds
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Road Damage (iWatchRoad)</span>
              <span className="text-indigo-400 font-bold">{potholeThreshold}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={potholeThreshold}
              onChange={(e) => setPotholeThreshold(parseInt(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <p className="text-[11px] text-slate-400">
              Minimum confidence required to log pothole observations from vehicle dashcams.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Solid Waste (TrashMonkey)</span>
              <span className="text-indigo-400 font-bold">{garbageThreshold}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={garbageThreshold}
              onChange={(e) => setGarbageThreshold(parseInt(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <p className="text-[11px] text-slate-400">
              Threshold to distinguish legal bins from illegal roadside blackspot overflows.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Streetlight Outage (YOLOR)</span>
              <span className="text-indigo-400 font-bold">{streetlightThreshold}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={streetlightThreshold}
              onChange={(e) => setStreetlightThreshold(parseInt(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <p className="text-[11px] text-slate-400">
              Confidence threshold required before classifying unlit high-mast lamps as defective.
            </p>
          </div>
        </div>
      </div>

      {/* ── Demo Dataset Operations ── */}
      <div className="card p-5 space-y-4 border-indigo-500/30 bg-indigo-950/10">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-white">
            Hackathon Demonstration Dataset Control
          </h2>
        </div>

        <p className="text-xs text-slate-300">
          Reset all city infrastructure, contractor profiles, maintenance work orders, citizen complaints, and chronological City Memory ledger to the calibrated 24-hour hackathon demonstration scenario.
        </p>

        <button
          onClick={handleSeed}
          disabled={seeding}
          className="btn-primary text-xs gap-2"
        >
          <Sparkles className={`w-3.5 h-3.5 ${seeding ? 'animate-spin' : ''}`} />
          {seeding ? 'Re-seeding Scenario…' : 'Reset & Re-seed Demo Scenario'}
        </button>
      </div>
    </div>
  );
}

export default Settings;
