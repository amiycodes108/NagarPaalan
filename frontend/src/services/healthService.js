import api from './api';

/**
 * Fetch overall API health status.
 * GET /api/v1/health
 */
export async function getHealth() {
  const response = await api.get('/health');
  return response.data;
}

/**
 * Fetch database health status.
 * GET /api/v1/health/db
 */
export async function getDbHealth() {
  const response = await api.get('/health/db');
  return response.data;
}

/**
 * Fetch Redis health status.
 * GET /api/v1/health/redis
 */
export async function getRedisHealth() {
  const response = await api.get('/health/redis');
  return response.data;
}
