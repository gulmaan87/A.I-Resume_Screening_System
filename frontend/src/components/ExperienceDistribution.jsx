function ExperienceDistribution({ distribution = {} }) {
  const entries = Object.entries(distribution);
  if (!entries.length) {
    return null;
  }

  const max = Math.max(...entries.map(([, value]) => value));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700">Experience Distribution</h3>
      <div className="mt-4 space-y-3">
        {entries.map(([bucket, value]) => (
          <div key={bucket} className="space-y-1">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>{bucket}</span>
              <span>{value}</span>
            </div>
            <div className="h-2.5 w-full rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-primary-500 transition-all"
                style={{ width: `${(value / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ExperienceDistribution;

