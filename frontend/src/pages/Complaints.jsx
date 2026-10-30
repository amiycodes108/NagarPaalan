import React, { useEffect, useState } from 'react';
import { civicApi } from '../services/api';
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  ExternalLink,
  FileText,
  Filter,
  Link as LinkIcon,
  MapPin,
  MessageSquare,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
  User,
  X,
} from 'lucide-react';

function Complaints() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [showNewModal, setShowNewModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // New Complaint Form
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Pothole',
    latitude: 12.9734,
    longitude: 77.6112,
    citizen_name: '',
    citizen_phone: '',
    channel: 'Citizen App',
  });

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const data = await civicApi.getComplaints();
      setComplaints(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleSelectComplaint = async (complaint) => {
    try {
      const detail = await civicApi.getComplaint(complaint.id);
      setSelectedComplaint(detail);
    } catch (err) {
      setSelectedComplaint(complaint);
    }
  };

  const handleConfirmLink = async (issueId) => {
    if (!selectedComplaint) return;
    try {
      setActionLoading(true);
      await civicApi.linkComplaintToIssue(selectedComplaint.id, {
        issue_id: issueId,
        review_notes: 'Administrator confirmed match via explainable scoring.',
      });
      fetchComplaints();
      const updated = await civicApi.getComplaint(selectedComplaint.id);
      setSelectedComplaint(updated);
    } catch (err) {
      alert(`Error linking complaint: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePromoteToIssue = async () => {
    if (!selectedComplaint) return;
    try {
      setActionLoading(true);
      await civicApi.promoteComplaintToIssue(selectedComplaint.id, {
        severity: 'High',
      });
      fetchComplaints();
      const updated = await civicApi.getComplaint(selectedComplaint.id);
      setSelectedComplaint(updated);
    } catch (err) {
      alert(`Error creating issue: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmitNew = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      const created = await civicApi.createComplaint(formData);
      setShowNewModal(false);
      setFormData({
        title: '',
        description: '',
        category: 'Pothole',
        latitude: 12.9734,
        longitude: 77.6112,
        citizen_name: '',
        citizen_phone: '',
        channel: 'Citizen App',
      });
      fetchComplaints();
      handleSelectComplaint(created);
    } catch (err) {
      alert(`Submission error: ${err.message}`);
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
              Citizen Grievances & Duplicate Intelligence
            </h1>
            <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Explainable AI Match Active
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Multi-channel report ingestion, semantic similarity matching, and administrative issue consolidation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowNewModal(true)}
            className="btn-primary text-xs gap-2"
          >
            <Plus className="w-4 h-4" />
            File New Grievance
          </button>
          <button
            onClick={fetchComplaints}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Complaints List & Detail Pane ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Complaints Table/List */}
        <div className="lg:col-span-2 card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">
                Intake Grievance Ledger ({complaints.length})
              </h2>
            </div>
            <span className="text-xs text-slate-400">Click row for Duplicate Match Details</span>
          </div>

          <div className="divide-y divide-slate-800">
            {complaints.map((c) => {
              const isSelected = selectedComplaint?.id === c.id;
              const hasMatch = c.match_status === 'Matched Existing';
              const isConfirmed = c.match_status === 'Confirmed Match';

              return (
                <div
                  key={c.id}
                  onClick={() => handleSelectComplaint(c)}
                  className={`p-4 rounded-xl cursor-pointer transition flex items-start justify-between gap-4 ${
                    isSelected
                      ? 'bg-indigo-950/40 border border-indigo-500/50'
                      : 'hover:bg-slate-800/40'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-indigo-400">
                        {c.ticket_number}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {c.channel}
                      </span>

                      {hasMatch && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          AI Match: {Math.round(c.match_score)}%
                        </span>
                      )}

                      {isConfirmed && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          Linked to Issue
                        </span>
                      )}
                    </div>

                    <div className="text-sm font-bold text-white">
                      {c.title}
                    </div>

                    <p className="text-xs text-slate-400 line-clamp-1">
                      {c.description}
                    </p>

                    <div className="text-[11px] text-slate-500 flex items-center gap-3 pt-1">
                      <span>Reporter: {c.citizen_name}</span>
                      <span>•</span>
                      <span>Category: {c.category}</span>
                      <span>•</span>
                      <span>{new Date(c.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <ChevronRight className="w-5 h-5 text-slate-500 mt-2 flex-shrink-0" />
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Explainable AI Duplicate Match Modal / Panel */}
        <div className="card p-5 space-y-5">
          {!selectedComplaint ? (
            <div className="py-24 text-center text-slate-500 text-xs">
              Select any grievance from the list to view its explainable AI match criteria, distance, and administrative review actions.
            </div>
          ) : (
            <div className="space-y-5">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-xs text-indigo-400 font-bold">
                    {selectedComplaint.ticket_number}
                  </span>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    {selectedComplaint.title}
                  </h3>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full font-semibold bg-slate-800 text-slate-300">
                  {selectedComplaint.status}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
                <p>{selectedComplaint.description}</p>
                <div className="mt-2 text-[11px] text-slate-400">
                  📍 Coordinates: {selectedComplaint.latitude}, {selectedComplaint.longitude}
                </div>
              </div>

              {/* Explainable Match Scoring Breakdown */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-white">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>Explainable Match Evaluation</span>
                  </div>
                  {selectedComplaint.match_score && (
                    <span className="text-xs font-extrabold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                      Score: {selectedComplaint.match_score}%
                    </span>
                  )}
                </div>

                {selectedComplaint.matched_candidates?.length > 0 ? (
                  <div className="space-y-3">
                    {selectedComplaint.matched_candidates.map((cand, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl border border-indigo-500/30 bg-indigo-950/20 space-y-2.5 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-indigo-300">
                            Candidate {cand.target_type.toUpperCase()}: {cand.target_code}
                          </span>
                          <span className="font-bold text-white">
                            Match: {cand.overall_match_score}%
                          </span>
                        </div>

                        <div className="text-slate-300 font-medium">
                          {cand.target_title}
                        </div>

                        {/* Breakdown pills */}
                        <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                          <span className="p-1 rounded bg-slate-900 text-slate-300">
                            Dist: <b>{cand.distance_meters}m</b>
                          </span>
                          <span className="p-1 rounded bg-slate-900 text-slate-300">
                            Semantic: <b>{Math.round(cand.semantic_similarity * 100)}%</b>
                          </span>
                        </div>

                        {/* Detailed Reasons */}
                        <div className="space-y-1 pt-1 border-t border-slate-800/80 text-[11px] text-slate-400">
                          {cand.reasons.map((r, ri) => (
                            <div key={ri} className="flex items-start gap-1">
                              <span className="text-indigo-400 font-semibold">{r.criterion}:</span>
                              <span>{r.explanation}</span>
                            </div>
                          ))}
                        </div>

                        {/* Action: Link to this candidate if target is an issue */}
                        {cand.target_type === 'issue' && selectedComplaint.status !== 'Linked to Issue' && (
                          <button
                            onClick={() => handleConfirmLink(cand.target_id)}
                            disabled={actionLoading}
                            className="btn-primary w-full text-xs gap-1.5 mt-2"
                          >
                            <LinkIcon className="w-3.5 h-3.5" />
                            Confirm Duplicate & Link to Issue
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-lg bg-slate-900 text-slate-400 text-xs">
                    No duplicate clusters found. This appears to be a distinct new civic report.
                  </div>
                )}
              </div>

              {/* Administrative Override Actions */}
              {selectedComplaint.status !== 'Linked to Issue' && (
                <div className="pt-2 border-t border-slate-800 space-y-2">
                  <div className="text-xs font-semibold text-slate-400">Administrative Override:</div>
                  <button
                    onClick={handlePromoteToIssue}
                    disabled={actionLoading}
                    className="btn-secondary w-full text-xs gap-2"
                  >
                    <Plus className="w-3.5 h-3.5 text-emerald-400" />
                    Create Distinct Physical Issue
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── New Complaint Modal ── */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="card p-6 w-full max-w-lg space-y-4 border border-slate-700 bg-slate-900 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">
                Register Citizen Grievance
              </h3>
              <button
                onClick={() => setShowNewModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitNew} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Grievance Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Broken pothole near Trinity Metro"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Detailed Description</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Describe location, depth, hazards..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
                    <option value="Pothole">Pothole / Road Damage</option>
                    <option value="Streetlight">Streetlight Failure</option>
                    <option value="Garbage">Garbage / Solid Waste</option>
                    <option value="Drainage">Drainage / Overflow</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Channel</label>
                  <select
                    value={formData.channel}
                    onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  >
                    <option value="Citizen App">Citizen App</option>
                    <option value="WhatsApp Helpline">WhatsApp Helpline</option>
                    <option value="Web Portal">Web Portal</option>
                    <option value="Call Center">Call Center</option>
                  </select>
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

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Citizen Name</label>
                  <input
                    type="text"
                    placeholder="Citizen name"
                    value={formData.citizen_name}
                    onChange={(e) => setFormData({ ...formData, citizen_name: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Phone</label>
                  <input
                    type="text"
                    placeholder="+91..."
                    value={formData.citizen_phone}
                    onChange={(e) => setFormData({ ...formData, citizen_phone: e.target.value })}
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
                  {actionLoading ? 'Analyzing & Saving…' : 'Submit Grievance'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Complaints;
