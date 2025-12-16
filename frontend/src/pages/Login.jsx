import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../lib/api.js";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const { data } = await apiClient.post("/api/auth/login", {
        credentials: { email, password },
      });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      navigate("/");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Login failed. Please check your credentials."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-700 to-dark-900 px-4 py-8">
      <div className="glass-strong max-w-md w-full p-8 rounded-2xl shadow-glassxl border glass-border-light dark:border-dark-700 flex flex-col gap-8 text-slate-200">
        <div className="space-y-3">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-accent-vibrant via-primary-500 to-accent-purple bg-clip-text text-transparent">Sign in</h2>
          <p className="text-sm text-slate-300">
            Enter your credentials to access the system
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-7">
          <div>
            <label htmlFor="email" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 backdrop-blur focus:ring-2 focus:ring-accent-vibrant focus:border-accent-vibrant transition placeholder:text-slate-400 focus:shadow-glassxl"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-xs font-semibold mb-1 text-slate-300 uppercase tracking-wide">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-xl border border-dark-700 bg-glass/80 px-3 py-2 text-base text-slate-200 backdrop-blur focus:ring-2 focus:ring-accent-vibrant focus:border-accent-vibrant transition placeholder:text-slate-400 focus:shadow-glassxl"
              placeholder="••••••••"
            />
          </div>
          {error && (
            <div className="rounded-lg border border-red-400 bg-red-900/40 px-4 py-2 text-sm text-red-200">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full rounded-xl bg-gradient-to-br from-accent-vibrant via-primary-600 to-primary-400 px-4 py-3 text-base font-bold uppercase tracking-wider text-white shadow-xl hover:scale-[1.02] hover:shadow-glassxl focus:outline-none focus:ring-2 focus:ring-accent-vibrant focus:ring-offset-2 transition-all duration-150 disabled:opacity-60"
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="text-center text-xs text-slate-400">
          Don&apos;t have an account?{' '}
          <Link to="/register" className="font-bold text-accent-vibrant hover:text-accent-purple transition-colors">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;

