import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  Camera,
  CheckCircle2,
  Cpu,
  Eye,
  FileImage,
  Layers,
  MapPin,
  MapPinOff,
  RefreshCw,
  Shield,
  Sparkles,
  Tag,
  Upload,
} from 'lucide-react';

function CivicVision() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('iwatchroad-v2-heuristic');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [detections, setDetections] = useState([]);
  const [recentObservations, setRecentObservations] = useState([]);

  // Explicit GPS Input (Optional)
  const [manualLat, setManualLat] = useState('');
  const [manualLon, setManualLon] = useState('');

  useEffect(() => {
    civicApi.getAiModels().then(setModels).catch(console.error);
    fetchObservations();
  }, []);

  const fetchObservations = async () => {
    try {
      const data = await civicApi.getObservations({ channel: 'Civic Vision' });
      setRecentObservations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetections([]);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append(
        'category_hint',
        selectedModel.includes('trash')
          ? 'garbage'
          : selectedModel.includes('street')
          ? 'streetlight'
          : 'pothole'
      );
      formData.append('source_channel', 'Civic Vision');

      // Only attach coordinates if user explicitly typed them
      if (manualLat && manualLon) {
        formData.append('latitude', manualLat);
        formData.append('longitude', manualLon);
      }

      const results = await civicApi.analyzeImage(formData);
      setDetections(results);
      fetchObservations();
    } catch (err) {
      alert(`Inference error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Civic Vision & Multi-Model Inference
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              Heuristic Engine • Weights Standby
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Heuristic visual anomaly detection, verifiable EXIF GPS parsing, and physical asset mapping.
          </p>
        </div>
      </div>

      {/* ── Transparency Notice ── */}
      <div className="p-4 rounded-xl border border-purple-500/30 bg-purple-950/20 text-xs text-slate-300 space-y-1">
        <div className="flex items-center gap-2 font-bold text-purple-300">
          <Shield className="w-4 h-4 text-purple-400" />
          <span>Inference Engine Transparency Note</span>
        </div>
        <p>
          Current detections execute via <b>Heuristic Computer Vision algorithms</b> (pavement luminance gradient & dark concavity ROI segmentation).
          Pretrained deep learning weights for <code>smlab-niser/iwatchroad</code>, <code>TrashMonkey</code>, and <code>YOLOR</code> are in standby mode awaiting model file placement.
        </p>
      </div>

      {/* ── Model Selector Grid ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {models.map((m) => {
          const isSelected = selectedModel === m.id;
          return (
            <div
              key={m.id}
              onClick={() => setSelectedModel(m.id)}
              className={`card p-4 cursor-pointer transition border ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-950/20 shadow-lg shadow-indigo-500/10'
                  : 'hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-white">{m.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {m.status.includes('Active') ? 'Active (Heuristic)' : m.status}
                </span>
              </div>
              <div className="text-[11px] text-slate-400 mb-2 font-mono">
                {m.architecture}
              </div>
              <div className="flex flex-wrap gap-1">
                {m.classes_detected.slice(0, 3).map((cls, i) => (
                  <span
                    key={i}
                    className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-300"
                  >
                    {cls}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Inference Studio & Visualizer ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload & Inspect */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Photograph Upload & Geotagging
            </h2>
          </div>

          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 text-center transition cursor-pointer bg-slate-900/40 relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <FileImage className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <div className="text-xs font-semibold text-slate-200">
                {selectedFile ? selectedFile.name : 'Select or Drop Civic Photograph'}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                JPG, PNG. Reads genuine EXIF GPS tags if present in photo metadata.
              </p>
            </div>

            {/* Explicit Manual Coordinates Input (Optional) */}
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
              <div className="text-[11px] text-slate-400 font-semibold">
                Optional Manual Coordinates (If photo has no EXIF):
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <input
                  type="number"
                  step="0.0001"
                  placeholder="Latitude (e.g. 12.9733)"
                  value={manualLat}
                  onChange={(e) => setManualLat(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded p-2 text-white text-xs"
                />
                <input
                  type="number"
                  step="0.0001"
                  placeholder="Longitude (e.g. 77.6111)"
                  value={manualLon}
                  onChange={(e) => setManualLon(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded p-2 text-white text-xs"
                />
              </div>
            </div>

            {previewUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-700 max-h-64 flex justify-center bg-black">
                <img
                  src={previewUrl}
                  alt="Inspection preview"
                  className="max-h-64 object-contain"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={!selectedFile || loading}
              className="btn-primary w-full text-xs gap-2"
            >
              <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Running AI Vision Inference…' : 'Execute Model Inference'}
            </button>
          </form>
        </div>

        {/* Normalized Detections Visualizer */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">
                Normalized Output & Provenance
              </h2>
            </div>
            <span className="text-xs text-slate-400 font-mono">Section 5 Standard</span>
          </div>

          {detections.length === 0 ? (
            <div className="py-16 text-center text-slate-500 text-xs">
              Upload an image on the left and run inference to inspect normalized bounding boxes, defect classification, and verified GPS provenance.
            </div>
          ) : (
            <div className="space-y-4 animate-in fade-in">
              {detections[0]?.image_url && (
                <div className="rounded-lg overflow-hidden border border-indigo-500/40 shadow-lg">
                  <div className="bg-slate-900 px-3 py-1.5 text-[11px] font-semibold text-indigo-300 flex items-center justify-between">
                    <span>Annotated Output</span>
                    <span>Confidence: {Math.round(detections[0].confidence * 100)}%</span>
                  </div>
                  <img
                    src={detections[0].image_url}
                    alt="Annotated detection"
                    className="w-full max-h-56 object-cover bg-black"
                  />
                </div>
              )}

              <div className="space-y-2">
                {detections.map((d, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-slate-900 border border-slate-700/80 space-y-1.5 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white capitalize">
                        {d.category.replace('_', ' ')}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-500/20 text-indigo-300">
                        {Math.round(d.confidence * 100)}% Confidence
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
                      <span>Model: <b>{d.model_name}</b></span>
                      <span>Engine: <b>{d.inference_engine_type}</b></span>
                    </div>

                    {/* GPS Provenance Badge */}
                    <div className="pt-1">
                      {d.is_located ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                          <MapPin className="w-3 h-3" />
                          Provenance: {d.location_provenance} ({d.latitude?.toFixed(4)}, {d.longitude?.toFixed(4)})
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-semibold">
                          <MapPinOff className="w-3 h-3" />
                          Unlocated (No GPS in EXIF or manual input)
                        </span>
                      )}
                    </div>

                    {d.defect_classification && (
                      <p className="text-[11px] text-amber-300 bg-amber-950/30 px-2 py-1 rounded">
                        Class: {d.defect_classification}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CivicVision;
