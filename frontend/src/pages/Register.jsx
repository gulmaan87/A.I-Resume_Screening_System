import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../lib/api.js";

function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }
    if (!formData.full_name || formData.full_name.trim().length === 0) {
      setError("Full name is required");
      return;
    }
    setIsLoading(true);
    try {
      const registrationData = {
        user_data: {
          email: formData.email.trim(),
          password: formData.password,
          full_name: formData.full_name.trim(),
        },
      };
      await apiClient.post("/api/auth/register", registrationData, {
        headers: { "Content-Type": "application/json" },
      });
      const { data } = await apiClient.post("/api/auth/login", {
        credentials: {
          email: registrationData.user_data.email,
          password: registrationData.user_data.password,
        },
      });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      const errorData = err.response?.data;
      let errorMessage = "Registration failed. Please try again.";
      if (!err.response) {
        errorMessage = "Network error. Please check your connection and try again.";
      } else if (errorData) {
        if (errorData.errors && Array.isArray(errorData.errors)) {
          const validationErrors = errorData.errors.map(
            (e) => `${e.loc?.slice(1).join(".") || "field"}: ${e.msg}`
          ).join(", ");
          errorMessage = `Validation error: ${validationErrors}`;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (err.response.status === 400) {
          errorMessage = "Bad request. Please check your input.";
        } else if (err.response.status === 500) {
          errorMessage = "Server error. Please try again later.";
        }
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-700 to-dark-900 py-8 px-4">
      <div className="glass-strong max-w-md w-full p-8 rounded-2xl shadow-glassxl border glass-border-light dark:border-dark-700 flex flex-col gap-8 text-slate-200">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-accent-purple via-primary-400 to-accent-vibrant bg-clip-text text-transparent mb-1">Create account</h2>
          <p className="text-sm text-slate-300">Sign up to get started with AI Resume Screening</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-7">
          <div>
            <label htmlFor="full_name" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">Full Name</label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              required
              value={formData.full_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 placeholder:text-slate-400 backdrop-blur focus:ring-2 focus:ring-accent-purple focus:border-accent-purple focus:shadow-glass transition"
              placeholder="John Doe"
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 placeholder:text-slate-400 backdrop-blur focus:ring-2 focus:ring-primary-400 focus:border-primary-400 focus:shadow-glass transition"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 placeholder:text-slate-400 backdrop-blur focus:ring-2 focus:ring-accent-vibrant focus:border-accent-vibrant focus:shadow-glass transition"
              placeholder="••••••••"
            />
            <p className="text-xs text-slate-400 mt-1">Must be at least 8 characters</p>
          </div>
          <div>
            <label htmlFor="confirmPassword" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 placeholder:text-slate-400 backdrop-blur focus:ring-2 focus:ring-accent-vibrant focus:border-accent-vibrant focus:shadow-glass transition"
              placeholder="••••••••"
            />
          </div>
          {error && (
            <div className="rounded-lg border border-red-400 bg-red-900/40 px-4 py-2 text-sm text-red-200 ">{error}</div>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full rounded-xl bg-gradient-to-br from-primary-600 via-accent-purple to-accent-vibrant px-4 py-3 text-base font-bold uppercase tracking-wider text-white shadow-xl hover:scale-[1.02] hover:shadow-glassxl focus:outline-none focus:ring-2 focus:ring-accent-vibrant focus:ring-offset-2 transition-all duration-150 disabled:opacity-60"
          >
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>
        <p className="text-center text-xs text-slate-400">
          Already have an account?{' '}
          <Link to="/login" className="font-bold text-accent-vibrant hover:text-accent-purple transition-colors">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

