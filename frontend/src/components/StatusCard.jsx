function StatusCard({ name, status, latency }) {
  const normalizedStatus = (status || '').toLowerCase();

  const statusConfig = {
    healthy: {
      dotClass: 'status-dot-healthy',
      label: 'Healthy',
      labelClass: 'text-emerald-400',
      borderClass: 'border-emerald-500/20',
      bgClass: 'bg-emerald-500/5',
    },
    ok: {
      dotClass: 'status-dot-healthy',
      label: 'Healthy',
      labelClass: 'text-emerald-400',
      borderClass: 'border-emerald-500/20',
      bgClass: 'bg-emerald-500/5',
    },
    unhealthy: {
      dotClass: 'status-dot-unhealthy',
      label: 'Unhealthy',
      labelClass: 'text-red-400',
      borderClass: 'border-red-500/20',
      bgClass: 'bg-red-500/5',
    },
    error: {
      dotClass: 'status-dot-unhealthy',
      label: 'Error',
      labelClass: 'text-red-400',
      borderClass: 'border-red-500/20',
      bgClass: 'bg-red-500/5',
    },
    checking: {
      dotClass: 'status-dot-checking',
      label: 'Checking…',
      labelClass: 'text-amber-400',
      borderClass: 'border-amber-500/20',
      bgClass: 'bg-amber-500/5',
    },
  };

  const config = statusConfig[normalizedStatus] || {
    dotClass: 'status-dot bg-slate-500',
    label: status || 'Unknown',
    labelClass: 'text-slate-400',
    borderClass: 'border-slate-700/50',
    bgClass: '',
  };

  // Icon per service
  const icons = {
    'API Server': (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
      </svg>
    ),
    Database: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
      </svg>
    ),
    Redis: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
  };

  return (
    <div className={`card-hover p-5 ${config.borderClass} ${config.bgClass}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-slate-400">
            {icons[name] || (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            )}
          </div>
          <h3 className="text-sm font-semibold text-white">{name}</h3>
        </div>
      </div>

      {/* Status Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={config.dotClass} />
          <span className={`text-sm font-medium ${config.labelClass}`}>
            {config.label}
          </span>
        </div>

        {latency != null && (
          <span className="text-xs text-slate-500 font-mono">
            {typeof latency === 'number' ? `${latency.toFixed(0)}ms` : latency}
          </span>
        )}
      </div>
    </div>
  );
}

export default StatusCard;
