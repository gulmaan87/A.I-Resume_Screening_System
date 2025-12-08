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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    // Validate full name
    if (!formData.full_name || formData.full_name.trim().length === 0) {
      setError("Full name is required");
      return;
    }

    setIsLoading(true);

    try {
      // Register the user - ensure full_name is trimmed and not empty
      const registrationData = {
        user_data: {
          email: formData.email.trim(),
          password: formData.password,
          full_name: formData.full_name.trim(),
        },
      };
      
      await apiClient.post("/api/auth/register", registrationData, {
        headers: {
          "Content-Type": "application/json"
        }
      });

      // After successful registration, automatically log them in
      const { data } = await apiClient.post("/api/auth/login", {
        email: registrationData.email,
        password: registrationData.password,
      });

      // Store tokens in localStorage
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      // Redirect to dashboard
      navigate("/dashboard");
    } catch (err) {
      console.error("Registration error:", err);
      console.error("Error response:", err.response);
      
      // Handle different error response formats
      const errorData = err.response?.data;
      let errorMessage = "Registration failed. Please try again.";
      
      // Network error (no response)
      if (!err.response) {
        errorMessage = "Network error. Please check your connection and try again.";
      }
      // Server responded with error
      else if (errorData) {
        // FastAPI validation errors (422)
        if (errorData.errors && Array.isArray(errorData.errors)) {
          const validationErrors = errorData.errors.map(e => {
            const field = e.loc?.slice(1).join(".") || "field"; // Remove 'body' from path
            return `${field}: ${e.msg}`;
          }).join(", ");
          errorMessage = `Validation error: ${validationErrors}`;
        }
        // Standard error messages
        else if (errorData.detail) {
          errorMessage = errorData.detail;
        }
        else if (errorData.message) {
          errorMessage = errorData.message;
        }
        // Check status code for specific errors
        else if (err.response.status === 400) {
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
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Create account</h2>
          <p className="mt-2 text-sm text-slate-500">
            Sign up to get started with AI Resume Screening
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="full_name"
              className="block text-sm font-medium text-slate-700"
            >
              Full Name
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              required
              value={formData.full_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-slate-700"
            >
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-slate-700"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="••••••••"
            />
            <p className="mt-1 text-xs text-slate-500">
              Must be at least 8 characters
            </p>
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-slate-700"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

