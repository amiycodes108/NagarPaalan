import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Building2,
  Camera,
  Cpu,
  DollarSign,
  FileText,
  Flame,
  HardHat,
  History,
  Layers,
  MapPin,
  Menu,
  Repeat,
  Server,
  Settings as SettingsIcon,
  ShieldAlert,
  Sparkles,
  Video,
  Wrench,
  X,
  Zap,
} from 'lucide-react';
import { civicApi } from '../services/api';

const navGroups = [
  {
    title: 'Civic Operations',
    items: [
      { to: '/', label: 'Overview', icon: Activity },
      { to: '/complaints', label: 'Complaints', icon: FileText },
      { to: '/infrastructure', label: 'Infrastructure Registry', icon: Building2 },
      { to: '/maintenance', label: 'Maintenance', icon: Wrench },
    ],
  },
  {
    title: 'City Memory & Spatial',
    items: [
      { to: '/city-memory', label: 'City Memory', icon: History, highlight: true },
      { to: '/city-map', label: 'City Map', icon: MapPin },
      { to: '/hotspots', label: 'Hotspot Analysis', icon: Flame },
    ],
  },
  {
    title: 'AI Intelligence',
    items: [
      { to: '/dashcam', label: 'Dashcam Intelligence', icon: Video },
      { to: '/civic-vision', label: 'Civic Vision', icon: Camera },
      { to: '/models', label: 'Data & Models', icon: Cpu },
    ],
  },
  {
    title: 'Governance & Administration',
    items: [
      { to: '/finances', label: 'Financial Intelligence', icon: DollarSign },
      { to: '/contractors', label: 'Contractor Management', icon: HardHat },
      { to: '/settings', label: 'Settings', icon: SettingsIcon },
    ],
  },
];

function MainLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const location = useLocation();

  const handleSimulateRecurrence = async () => {
    try {
      setSimulating(true);
      const res = await civicApi.triggerRecurrence();
      alert(`⚡ Recurrence Ingested!\nAsset: ${res.asset} (${res.asset_code})\nRisk Escalate: ${res.risk_level} (${res.new_risk_score}/10)\nReason: ${res.risk_factors?.[0]}`);
      window.location.reload();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  const handleResetDemo = async () => {
    try {
      await civicApi.seedDemo();
      alert('🌱 Demonstration scenario reset & seeded successfully.');
      window.location.reload();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100">
      {/* ── Desktop Sidebar ── */}
      <aside className="hidden lg:flex flex-col w-64 bg-slate-900/90 border-r border-slate-800 backdrop-blur-md sticky top-0 h-screen overflow-y-auto">
        {/* Brand */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base tracking-wide text-white flex items-center gap-1.5">
              <span>NAGARPAALAN</span>
              <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/30">AI</span>
            </div>
            <div className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">
              City Memory Platform
            </div>
          </div>
        </div>

        {/* Navigation Groups */}
        <div className="flex-1 px-3 py-4 space-y-6">
          {navGroups.map((group, gi) => (
            <div key={gi} className="space-y-1">
              <div className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                {group.title}
              </div>
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.to;

                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                      isActive
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                        : item.highlight
                        ? 'text-red-400 hover:bg-slate-800/80 hover:text-red-300'
                        : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : item.highlight ? 'text-red-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                    {item.highlight && (
                      <span className="ml-auto w-1.5 h-1.5 rounded-full bg-red-400 animate-ping" />
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </div>

        {/* Sidebar Footer Demo Controls */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/40 space-y-2">
          <button
            onClick={handleSimulateRecurrence}
            disabled={simulating}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-red-600/20 text-red-300 hover:bg-red-600/30 border border-red-500/30 text-[11px] font-bold transition"
          >
            <Zap className={`w-3.5 h-3.5 ${simulating ? 'animate-spin' : ''}`} />
            {simulating ? 'Simulating…' : 'Simulate Recurrence'}
          </button>
          <button
            onClick={handleResetDemo}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white text-[10px] transition"
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            Reset Demo Dataset
          </button>
        </div>
      </aside>

      {/* ── Main Viewport ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-4 sm:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="hidden sm:block">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Municipal Command & Operations
              </span>
              <span className="text-[11px] text-slate-400 ml-2">
                City Memory v0.1 • 13 Modules Active
              </span>
            </div>
          </div>

          {/* Right Header Status & Controls */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-semibold text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>City Infrastructure Online</span>
            </div>
          </div>
        </header>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-slate-900 border-b border-slate-800 px-4 py-4 space-y-4">
            {navGroups.map((g, gi) => (
              <div key={gi} className="space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  {g.title}
                </div>
                <div className="grid grid-cols-2 gap-1 pt-1">
                  {g.items.map((it) => (
                    <NavLink
                      key={it.to}
                      to={it.to}
                      onClick={() => setMobileMenuOpen(false)}
                      className="px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-slate-800"
                    >
                      {it.label}
                    </NavLink>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Content Body */}
        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
