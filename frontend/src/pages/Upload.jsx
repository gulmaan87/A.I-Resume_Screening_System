import { useState } from "react";
import FileUpload from "../components/FileUpload.jsx";
import ScoreBadge from "../components/ScoreBadge.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import apiClient from "../lib/api.js";

function UploadPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (values, onSuccess) => {
    setIsSubmitting(true);
    setError("");
    setResult(null);
    try {
      const formData = new FormData();
      const file = values.resume[0];
      formData.append("resume", file);
      if (values.job_description) formData.append("job_description", values.job_description);
      if (values.candidate_name) formData.append("candidate_name", values.candidate_name);
      if (values.background) formData.append("background", values.background);

      const { data } = await apiClient.post("/api/resumes", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setResult(data);
      onSuccess?.();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to analyze resume. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <FileUpload onSubmit={handleSubmit} isSubmitting={isSubmitting} />

      {isSubmitting && <LoadingSpinner label="Extracting resume insights..." />}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {result && (
        <div className="grid gap-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-800">{result.full_name}</h3>
                <p className="text-sm text-slate-500">{result.email || "Email not detected"}</p>
              </div>
              <ScoreBadge category={result.category} score={result.score.total_ai_score} />
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-700">Summary</h4>
              <p className="mt-1 text-sm text-slate-600">{result.summary || "No professional summary detected."}</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h4 className="text-sm font-semibold text-slate-700">Key Skills</h4>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.skills.slice(0, 10).map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-700">Missing Skills</h4>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.missing_skills.slice(0, 10).map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-5">
            <h4 className="text-sm font-semibold text-slate-700">AI Score Breakdown</h4>
            <ul className="space-y-3 text-sm text-slate-600">
              <li className="flex items-center justify-between">
                <span>Similarity</span>
                <span className="font-semibold">{result.score.similarity_score.toFixed(1)}%</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Skill Match</span>
                <span className="font-semibold">{result.score.skill_match_score.toFixed(1)}%</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Experience</span>
                <span className="font-semibold">{result.score.experience_score.toFixed(1)}%</span>
              </li>
            </ul>
            {result.metadata?.s3_url && (
              <div>
                <h5 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Download Link
                </h5>
                <a
                  href={result.metadata.s3_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-flex items-center text-xs font-semibold text-primary-600 hover:text-primary-500"
                >
                  View stored resume
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadPage;

