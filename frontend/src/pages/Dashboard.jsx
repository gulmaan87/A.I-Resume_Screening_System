import { useEffect, useState } from "react";
import CandidateTable from "../components/CandidateTable.jsx";
import AnalyticsCards from "../components/AnalyticsCards.jsx";
import ExperienceDistribution from "../components/ExperienceDistribution.jsx";
import SkillGapList from "../components/SkillGapList.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import apiClient from "../lib/api.js";

function DashboardPage() {
  const [data, setData] = useState({ candidates: [], analytics: {} });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const { data: response } = await apiClient.get("/api/dashboard");
      setData(response);
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Candidate Intelligence Center</h2>
          <p className="text-sm text-slate-500">
            Track AI scores, missing skills, and pipeline health in real time.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-600 shadow-sm transition hover:bg-primary-50 hover:text-primary-600"
        >
          Refresh
        </button>
      </div>

      {isLoading && <LoadingSpinner label="Loading candidate analytics..." />}
      {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

      {!isLoading && !error && (
        <>
          <AnalyticsCards analytics={data.analytics} />

          <div className="grid gap-6 lg:grid-cols-2">
            <ExperienceDistribution distribution={data.analytics.experience_distribution} />
            <SkillGapList skills={data.analytics.common_missing_skills} />
          </div>

          <CandidateTable candidates={data.candidates} />
        </>
      )}
    </div>
  );
}

export default DashboardPage;

