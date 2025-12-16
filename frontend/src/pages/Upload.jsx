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
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
      onSuccess?.();
    } catch (err) {
      console.error("Upload error:", err);
      let errorMessage = "Failed to analyze resume. Please try again.";
      if (err.response?.data) {
        const errorData = err.response.data;
        if (errorData.message && typeof errorData.message === "string") {
          errorMessage = errorData.message;
        } else if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (typeof errorData.detail === "object" && errorData.detail !== null) {
          if (errorData.detail.exception_message) {
            errorMessage = errorData.detail.exception_message;
          } else if (errorData.detail.message) {
            errorMessage = errorData.detail.message;
          } else {
            errorMessage = `Error: ${errorData.detail.exception_type || "Unknown error"}`;
          }
        } else if (errorData.error) {
          errorMessage = typeof errorData.error === "string" ? errorData.error : "An error occurred";
        }
      } else if (err.message) {
        if (err.code === "ERR_NETWORK" || err.code === "ECONNREFUSED") {
          errorMessage = "Cannot connect to server. Please check if the backend is running.";
        } else {
          errorMessage = err.message;
        }
      }
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-8 ">
      <div className="glass-strong max-w-xl w-full mx-auto p-8 rounded-2xl shadow-glassxl border glass-border-light dark:border-dark-700">
        <FileUpload onSubmit={handleSubmit} isSubmitting={isSubmitting} />
        {isSubmitting && <LoadingSpinner label="Extracting resume insights..." />}
        {error && (
          <div className="mt-6 rounded-lg border border-red-400 bg-red-900/40 px-4 py-2 text-sm text-red-200 font-bold text-center shadow-lg animate-pulse">
            {error}
          </div>
        )}
        {result && (
          <div className="mt-8 p-6 rounded-2xl glass shadow-glassxl border glass-border-light dark:border-dark-700 transition-all duration-300">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-2xl font-bold text-slate-100 mb-1">{result.full_name}</h3>
                <p className="text-xs text-slate-400">{result.email || "Email not detected"}</p>
              </div>
              <ScoreBadge category={result.category} score={result.score.total_ai_score} />
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Summary</h4>
              <p className="text-sm text-slate-200 mt-1 mb-3">{result.summary || "No professional summary detected."}</p>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-xs font-semibold uppercase text-slate-400 mb-1">Key Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {result.skills.slice(0, 10).map((skill) => (
                    <span key={skill} className="inline-flex items-center rounded-full bg-blue-800/40 px-3 py-1 text-xs font-medium text-accent-vibrant shadow-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-xs font-semibold uppercase text-slate-400 mb-1">Missing Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {result.missing_skills.slice(0, 10).map((skill) => (
                    <span key={skill} className="inline-flex items-center rounded-full bg-red-900/40 px-3 py-1 text-xs font-medium text-red-200">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-4 grid gap-4">
              <h5 className="text-xs text-slate-400 uppercase">AI Score Breakdown</h5>
              <ul className="space-y-2 text-sm text-slate-200">
                <li className="flex items-center justify-between">
                  <span>Similarity</span>
                  <span className="font-semibold text-accent-vibrant">{result.score.similarity_score.toFixed(1)}%</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Skill Match</span>
                  <span className="font-semibold text-primary-200">{result.score.skill_match_score.toFixed(1)}%</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Experience</span>
                  <span className="font-semibold text-accent-purple">{result.score.experience_score.toFixed(1)}%</span>
                </li>
              </ul>
              {result.metadata?.s3_url && (
                <div>
                  <h6 className="text-xs font-semibold tracking-wide text-slate-400">Download Link</h6>
                  <a
                    href={result.metadata.s3_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 text-xs font-semibold text-accent-vibrant hover:text-accent-purple transition-all"
                  >
                    View stored resume
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadPage;

