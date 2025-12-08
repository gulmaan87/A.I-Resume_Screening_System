import { ChartPieIcon, UserGroupIcon, LightBulbIcon, ArrowTrendingUpIcon } from "@heroicons/react/24/outline";

const icons = {
  average_score: <ChartPieIcon className="h-6 w-6 text-primary-500" />,
  strong_fit: <ArrowTrendingUpIcon className="h-6 w-6 text-green-500" />,
  medium_fit: <ArrowTrendingUpIcon className="h-6 w-6 text-yellow-500" />,
  weak_fit: <ArrowTrendingUpIcon className="h-6 w-6 text-red-500" />,
  missing_skills: <LightBulbIcon className="h-6 w-6 text-amber-500" />,
  total_candidates: <UserGroupIcon className="h-6 w-6 text-slate-500" />
};

function AnalyticsCards({ analytics }) {
  if (!analytics || !analytics.average_score) {
    return null;
  }

  const { average_score, category_counts = {}, common_missing_skills = [] } = analytics;

  const tiles = [
    {
      id: "average_score",
      label: "Average AI Score",
      value: `${average_score.toFixed(1)}%`
    },
    {
      id: "total_candidates",
      label: "Total Candidates",
      value: Object.values(category_counts).reduce((sum, count) => sum + count, 0)
    },
    {
      id: "strong_fit",
      label: "Strong Fits",
      value: category_counts["Strong Fit"] || 0
    },
    {
      id: "medium_fit",
      label: "Medium Fits",
      value: category_counts["Medium Fit"] || 0
    },
    {
      id: "weak_fit",
      label: "Weak Fits",
      value: category_counts["Weak Fit"] || 0
    },
    {
      id: "missing_skills",
      label: "Common Missing Skills",
      value: common_missing_skills.slice(0, 3).join(", ") || "N/A"
    }
  ];

  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {tiles.map((tile) => (
        <div
          key={tile.id}
          className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">{tile.label}</span>
            {icons[tile.id]}
          </div>
          <div className="pt-4 text-2xl font-semibold text-slate-800">{tile.value}</div>
        </div>
      ))}
    </div>
  );
}

export default AnalyticsCards;

