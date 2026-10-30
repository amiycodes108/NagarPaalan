import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(message));
  },
);

export const civicApi = {
  // Health
  getHealth: () => api.get('/health').then((r) => r.data),

  // Analytics & Overview
  getOverview: () => api.get('/analytics/overview').then((r) => r.data),
  getHotspots: () => api.get('/analytics/hotspots').then((r) => r.data),
  getFinances: () => api.get('/analytics/finances').then((r) => r.data),
  getRecurrenceAudit: () => api.get('/analytics/recurrence-audit').then((r) => r.data),

  // Assets
  getAssets: (params) => api.get('/assets', { params }).then((r) => r.data),
  getAsset: (id) => api.get(`/assets/${id}`).then((r) => r.data),
  getAssetTimeline: (id) => api.get(`/assets/${id}/timeline`).then((r) => r.data),
  createAsset: (data) => api.post('/assets', data).then((r) => r.data),

  // Issues
  getIssues: (params) => api.get('/issues', { params }).then((r) => r.data),
  createIssue: (data) => api.post('/issues', data).then((r) => r.data),
  updateIssue: (id, data) => api.patch(`/issues/${id}`, data).then((r) => r.data),

  // Complaints & Duplicate Detection
  getComplaints: (params) => api.get('/complaints', { params }).then((r) => r.data),
  getComplaint: (id) => api.get(`/complaints/${id}`).then((r) => r.data),
  createComplaint: (data) => api.post('/complaints', data).then((r) => r.data),
  linkComplaintToIssue: (id, data) => api.post(`/complaints/${id}/link-issue`, data).then((r) => r.data),
  promoteComplaintToIssue: (id, data) => api.post(`/complaints/${id}/create-issue`, data).then((r) => r.data),

  // AI Vision & Dashcam
  getAiModels: () => api.get('/vision/models').then((r) => r.data),
  getObservations: (params) => api.get('/vision/observations', { params }).then((r) => r.data),
  analyzeImage: (formData) =>
    api
      .post('/vision/analyze-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data),
  uploadDashcam: (formData) =>
    api
      .post('/vision/dashcam-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data),

  // Maintenance & Contractors
  getRepairs: (params) => api.get('/maintenance/repairs', { params }).then((r) => r.data),
  createRepair: (data) => api.post('/maintenance/repairs', data).then((r) => r.data),
  getContractors: () => api.get('/maintenance/contractors').then((r) => r.data),
  createContractor: (data) => api.post('/maintenance/contractors', data).then((r) => r.data),
  getInspections: (params) => api.get('/maintenance/inspections', { params }).then((r) => r.data),
  createInspection: (data) => api.post('/maintenance/inspections', data).then((r) => r.data),

  // Demonstration
  seedDemo: () => api.post('/demo/seed').then((r) => r.data),
  triggerRecurrence: () => api.post('/demo/trigger-recurrence').then((r) => r.data),
};

export default api;
