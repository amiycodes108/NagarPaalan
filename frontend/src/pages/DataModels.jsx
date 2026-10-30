import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  CheckCircle2,
  Code,
  Cpu,
  Database,
  ExternalLink,
  Layers,
  Lock,
  RefreshCw,
  Shield,
  Zap,
} from 'lucide-react';

function DataModels() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    civicApi.getAiModels()
      .then(setModels)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Pretrained Models & AI Adapter Catalog
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Zero Scratch Training • Section 5 Spec
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Open-source AI candidate models normalized through the unified NAGARPAALAN adapter abstraction layer.
          </p>
        </div>
      </div>

      {/* ── Architectural Standard Banner (Section 5) ── */}
      <div className="card p-5 border-cyan-500/30 bg-cyan-950/10 space-y-3">
        <div className="flex items-center gap-2 text-cyan-300 font-bold text-sm">
          <Shield className="w-5 h-5 text-cyan-400" />
          <span>Section 5 Normalized AI Contract</span>
        </div>
        <p className="text-xs text-slate-300">
          The core application remains completely decoupled from any single machine learning library or weights repository. Every integrated adapter translates upstream inferences into the common normalized structure:
        </p>
        <div className="p-3 rounded-lg bg-slate-950/80 font-mono text-[11px] text-cyan-300 border border-slate-800">
          category • confidence • bounding_box • frame_reference • timestamp • latitude • longitude • model_name • model_version • is_defect
        </div>
      </div>

      {/* ── Registered Models Grid ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {models.map((m) => (
          <div key={m.id} className="card p-5 space-y-4 border hover:border-indigo-500/50 transition">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold text-indigo-400 font-mono uppercase">
                  {m.task}
                </span>
                <h3 className="text-base font-bold text-white mt-1">
                  {m.name}
                </h3>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {m.status}
              </span>
            </div>

            <div className="text-xs space-y-1.5 text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <div><b>Architecture:</b> {m.architecture}</div>
              <div><b>Version:</b> {m.version}</div>
              <div><b>License:</b> {m.license}</div>
            </div>

            {/* Target Classes */}
            <div>
              <span className="text-[11px] font-semibold text-slate-400 block mb-1.5">
                Classes & Defect Types:
              </span>
              <div className="flex flex-wrap gap-1">
                {m.classes_detected.map((cls, i) => (
                  <span
                    key={i}
                    className="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-slate-300 border border-slate-700/60"
                  >
                    {cls}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <a
                href={m.source_candidate}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <span>Upstream Repository</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DataModels;
