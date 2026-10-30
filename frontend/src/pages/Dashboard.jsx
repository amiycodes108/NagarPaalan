import useHealth from '../hooks/useHealth';
import StatusCard from '../components/StatusCard';

function Dashboard() {
  const { health, loading, error, refetch } = useHealth();

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            System Status
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Real-time health overview of all NAGARPAALAN services.
          </p>
        </div>
        <button
          onClick={refetch}
          disabled={loading}
          className="btn-secondary gap-2 self-start sm:self-auto"
        >
          <svg
            className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182"
            />
          </svg>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {/* ── Error State ── */}
      {error && (
        <div className="card border-red-500/30 bg-red-500/5 p-4">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-300">
                Failed to fetch system health
              </p>
              <p className="text-xs text-red-400/70 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Loading State ── */}
      {loading && !health && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="h-4 w-24 bg-slate-700 rounded" />
              </div>
              <div className="h-3 w-16 bg-slate-700/60 rounded mt-2" />
            </div>
          ))}
        </div>
      )}

      {/* ── Data State ── */}
      {health && (
        <>
          {/* Version Badge */}
          {health.version && (
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                v{health.version}
              </span>
              {health.environment && (
                <span className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full bg-slate-700/50 text-slate-300 border border-slate-600/30">
                  {health.environment}
                </span>
              )}
            </div>
          )}

          {/* Status Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            <StatusCard
              name="API Server"
              status={health.api?.status || health.status || 'unknown'}
              latency={health.api?.latency}
            />
            <StatusCard
              name="Database"
              status={health.database?.status || 'unknown'}
              latency={health.database?.latency}
            />
            <StatusCard
              name="Redis"
              status={health.redis?.status || 'unknown'}
              latency={health.redis?.latency}
            />
          </div>

          {/* Timestamp */}
          {health.timestamp && (
            <p className="text-xs text-slate-500 text-right">
              Last checked: {new Date(health.timestamp).toLocaleString()}
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default Dashboard;
