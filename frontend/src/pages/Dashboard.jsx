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
      setError("Failed to load dashboard data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="flex justify-center py-8">
      <div className="glass-strong w-full max-w-6xl rounded-2xl shadow-glassxl px-8 py-10 border glass-border-light">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-6">
          <div className="relative z-0 flex flex-col items-start">
            <div className="absolute -inset-2 rounded-2xl bg-gradient-to-r from-accent-vibrant/60 via-primary-500/30 to-accent-purple/35 blur-2xl animate-pulse opacity-60 z-[-1]" aria-hidden="true"></div>
            <h2 className="text-4xl md:text-5xl font-black tracking-tight bg-gradient-to-br from-accent-vibrant via-primary-300 to-accent-purple bg-clip-text text-transparent drop-shadow-xl">
              Candidate Intelligence Center
            </h2>
            <div className="mt-3 px-4 py-2 rounded-xl border glass-border-light bg-dark-700/60 text-base md:text-lg text-slate-200 font-semibold shadow-glass">
              <span className="text-slate-300">Track AI scores, missing skills, and pipeline health in real time.</span>
            </div>
          </div>
          <button
            onClick={fetchData}
            className="rounded-lg border border-accent-vibrant/30 bg-glass/75 px-6 py-2 text-sm font-bold text-accent-vibrant shadow hover:bg-accent-vibrant hover:text-white hover:border-primary-400 focus:outline-none focus:ring-2 focus:ring-accent-vibrant transition-all"
          >
            Refresh
          </button>
        </div>
        {isLoading && (
          <div className="flex justify-center items-center my-12">
            <LoadingSpinner label="Loading candidate analytics..." />
          </div>
        )}
        {error && (
          <div className="my-6 rounded-lg border border-red-400 bg-red-900/40 px-4 py-2 text-center text-sm text-red-200 font-bold shadow animate-pulse">
            {error}
          </div>
        )}
        {!isLoading && !error && (
          <>
            <div className="mb-8">
              <AnalyticsCards analytics={data.analytics} />
            </div>
            <div className="grid gap-8 lg:grid-cols-2 mb-8">
              <div className="glass p-6 rounded-xl shadow-md border glass-border-light">
                <ExperienceDistribution distribution={data.analytics.experience_distribution} />
              </div>
              <div className="glass p-6 rounded-xl shadow-md border glass-border-light">
                <SkillGapList skills={data.analytics.common_missing_skills} />
              </div>
            </div>
            <div className="glass p-6 rounded-xl shadow-md border glass-border-light">
              <CandidateTable candidates={data.candidates} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;

