import ScoreBadge from "./ScoreBadge.jsx";

function CandidateTable({ candidates = [] }) {
  if (!candidates.length) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        No candidates have been screened yet. Upload a resume to get started.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-6 py-3 text-left font-semibold">Candidate</th>
            <th className="px-6 py-3 text-left font-semibold">Category</th>
            <th className="px-6 py-3 text-left font-semibold">Skill Match</th>
            <th className="px-6 py-3 text-left font-semibold">Experience</th>
            <th className="px-6 py-3 text-left font-semibold">Added</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-sm text-slate-600">
          {candidates.map((candidate) => (
            <tr key={candidate.id} className="hover:bg-primary-50/40">
              <td className="px-6 py-4">
                <div className="flex flex-col">
                  <span className="font-semibold text-slate-800">{candidate.full_name}</span>
                  <span className="text-xs text-slate-500">{candidate.email || "No email detected"}</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <ScoreBadge category={candidate.category} score={candidate.total_ai_score} />
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-20 rounded-full bg-primary-100">
                    <div
                      className="h-full rounded-full bg-primary-500"
                      style={{ width: `${Math.min(candidate.skill_match_score || 0, 100)}%` }}
                    />
                  </div>
                  <span>{(candidate.skill_match_score || 0).toFixed(1)}%</span>
                </div>
              </td>
              <td className="px-6 py-4">
                {candidate.experience_years != null ? `${candidate.experience_years.toFixed(1)} yrs` : "—"}
              </td>
              <td className="px-6 py-4 text-xs text-slate-500">
                {candidate.created_at ? new Date(candidate.created_at).toLocaleString() : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CandidateTable;

