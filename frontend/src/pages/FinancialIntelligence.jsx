import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  AlertTriangle,
  Building2,
  DollarSign,
  PieChart,
  RefreshCw,
  Repeat,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
  Wallet,
  Info,
  CheckCircle,
} from 'lucide-react';

function FinancialIntelligence() {
  const [finances, setFinances] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchFinances = async () => {
    try {
      setLoading(true);
      const data = await civicApi.getFinances();
      setFinances(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinances();
  }, []);

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Civic Financial Intelligence & Waste Audit
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Municipal CAPEX Intelligence
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Real-time public expenditure auditing, contractor disbursements, and identification of preventable recurrence waste.
          </p>
        </div>

        <button
          onClick={fetchFinances}
          className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700 self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── High-Level Financial Metrics ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 font-bold mb-2">
            <span>Total Maintenance Budget</span>
            <Wallet className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">
            ₹{((finances?.total_budget_allocated || 0) / 100000).toFixed(1)} Lakhs
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Allocated Municipal Infrastructure Grant
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 font-bold mb-2">
            <span>Actual Disbursed (Completed)</span>
            <DollarSign className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-400">
            ₹{((finances?.total_actual_expenditure ?? finances?.total_spent ?? 0) / 1000).toFixed(0)}k
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Verified completed work orders (Est. commitment: ₹{((finances?.total_estimated_expenditure ?? 0) / 1000).toFixed(0)}k)
          </div>
        </div>

        {/* The Core City Memory USP: Preventable Recurrence Cost */}
        <div className="card p-5 border-amber-500/30 bg-amber-950/20">
          <div className="flex items-center justify-between text-xs text-amber-300 font-bold mb-2">
            <span>Avoidable Repeat Waste</span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {finances?.avoidable_waste_percentage ?? 0}% of spend
            </span>
          </div>
          <div className="text-2xl font-extrabold text-amber-400">
            ₹{((finances?.avoidable_repeat_expenditure ?? finances?.preventable_recurrence_cost ?? 0) / 1000).toFixed(0)}k
          </div>
          <div className="text-[11px] text-amber-300/80 mt-1">
            Recurrence cycles &ge; 2 or warranty breach
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 font-bold mb-2">
            <span>Remaining Uncommitted</span>
            <TrendingUp className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-cyan-400">
            ₹{((finances?.remaining_budget || 0) / 100000).toFixed(1)} Lakhs
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Available fiscal reserve
          </div>
        </div>
      </div>

      {/* ── Category & Ward Breakdown ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spend by Infrastructure Category */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <PieChart className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Expenditure by Asset Category
            </h2>
          </div>

          <div className="space-y-3">
            {finances?.spend_by_category?.map((cat, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white">{cat.category}</span>
                  <span className="text-slate-300 font-mono">₹{cat.amount.toLocaleString()}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{
                      width: `${Math.min(100, (cat.amount / (finances.total_spent || 1)) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Spend by Ward */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Expenditure by Municipal Ward
            </h2>
          </div>

          <div className="space-y-3">
            {finances?.spend_by_ward?.map((w, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white">{w.ward}</span>
                  <span className="text-slate-300 font-mono">₹{w.amount.toLocaleString()}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{
                      width: `${Math.min(100, (w.amount / (finances.total_spent || 1)) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Audit Methodology & Explanations ── */}
      {finances?.metric_explanations?.length > 0 && (
        <div className="card p-6 space-y-4 border-slate-700/80 bg-slate-900/60">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Public Finance Audit Methodology & Transparency Notes
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            NAGARPAALAN AI enforces municipal accounting integrity: baseline maintenance is treated as legitimate civic investment, while avoidable waste is strictly isolated to repetitive patching cycles and warranty defaults.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {finances.metric_explanations.map((item, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm">{item.metric}</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    {item.audit_classification}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {item.explanation}
                </p>
                <div className="pt-1 text-[11px] font-mono text-slate-400 border-t border-slate-700/40">
                  <span className="text-slate-500 font-sans">Formula: </span>{item.formula_applied}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FinancialIntelligence;
