const colorMap = {
  "Strong Fit": "bg-green-100 text-green-700 border-green-300",
  "Medium Fit": "bg-yellow-100 text-yellow-700 border-yellow-300",
  "Weak Fit": "bg-red-100 text-red-700 border-red-300"
};

function ScoreBadge({ category, score }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${colorMap[category] ?? "bg-slate-100 text-slate-600 border-slate-300"}`}
    >
      <span>{category}</span>
      <span className="text-slate-500">|</span>
      <span>{score?.toFixed(1)}%</span>
    </span>
  );
}

export default ScoreBadge;

