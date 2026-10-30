import { useState, useEffect, useCallback } from 'react';
import { getHealth, getDbHealth, getRedisHealth } from '../services/healthService';

/**
 * Custom hook that fetches health data from all endpoints on mount.
 * Returns { health, loading, error, refetch }.
 */
function useHealth() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch all health endpoints in parallel
      const [apiHealth, dbHealth, redisHealth] = await Promise.allSettled([
        getHealth(),
        getDbHealth(),
        getRedisHealth(),
      ]);

      const apiData = apiHealth.status === 'fulfilled' ? apiHealth.value : null;
      const dbData = dbHealth.status === 'fulfilled' ? dbHealth.value : null;
      const redisData = redisHealth.status === 'fulfilled' ? redisHealth.value : null;

      // If the main health endpoint failed entirely, set error
      if (!apiData) {
        throw new Error(
          apiHealth.reason?.message || 'Unable to reach the API server',
        );
      }

      setHealth({
        status: apiData.status || 'unknown',
        version: apiData.version || null,
        environment: apiData.environment || null,
        timestamp: apiData.timestamp || new Date().toISOString(),
        api: {
          status: apiData.status || 'healthy',
          latency: apiData.latency,
        },
        database: {
          status: dbData?.status || (dbHealth.status === 'rejected' ? 'unhealthy' : 'unknown'),
          latency: dbData?.latency,
        },
        redis: {
          status: redisData?.status || (redisHealth.status === 'rejected' ? 'unhealthy' : 'unknown'),
          latency: redisData?.latency,
        },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return { health, loading, error, refetch: fetchHealth };
}

export default useHealth;
