import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import { CloudArrowUpIcon, ChartBarIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/outline";
import UploadPage from "./pages/Upload.jsx";
import DashboardPage from "./pages/Dashboard.jsx";
import LoginPage from "./pages/Login.jsx";
import RegisterPage from "./pages/Register.jsx";

const navLinkClass = ({ isActive }) =>
  `inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition border border-transparent shadow hover:shadow-lg backdrop-blur-md ${
    isActive
      ? "bg-accent-vibrant/80 text-white border-accent-vibrant ring-2 ring-accent-vibrant/30 shadow-glassxl"
      : "text-slate-300 hover:bg-dark-600/70 hover:text-white border-slate-700 hover:border-accent-vibrant"
  }`;

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const token = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  };

  // Add dark mode class to <html> (ensure this on first render)
  if (typeof document !== 'undefined') {
    document.documentElement.classList.add("dark");
  }

  return (
    <div className="min-h-screen relative bg-gradient-to-br from-dark-900 via-dark-700 to-dark-900 flex flex-col">
      {token && (
        <header className="glass strong fixed w-full z-30 shadow-xl dark:border-dark-800 border-b border-dark-800/80 dark:backdrop-blur-2xl dark:bg-backdrop dark:bg-opacity-85 ">
          <div className="mx-auto max-w-6xl flex justify-between items-center px-6 py-4 ">
            <div className="flex flex-col">
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-br from-accent-vibrant via-primary-500 to-accent-purple bg-clip-text text-transparent drop-shadow-xl select-none dark:drop-shadow-glassxl">
                AI Resume Screening
              </h1>
              <p className="text-xs text-slate-400 font-medium mt-1">
                Intelligent candidate insights for next-gen hiring teams
              </p>
            </div>
            <nav className="flex items-center gap-3">
              <NavLink to="/" end className={navLinkClass}>
                <CloudArrowUpIcon className="h-5 w-5" />
                Upload
              </NavLink>
              <NavLink to="/dashboard" className={navLinkClass}>
                <ChartBarIcon className="h-5 w-5" />
                Dashboard
              </NavLink>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 rounded-lg border border-red-400 px-4 py-2 text-sm font-medium text-red-200 hover:bg-red-700/80 hover:text-white transition shadow hover:shadow-2xl"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
                Logout
              </button>
            </nav>
          </div>
        </header>
      )}
      <main
        className={`flex-grow flex justify-center pt-28 pb-16 transition-all duration-300 ${token ? "px-2" : ""}`}
      >
        <div className="w-full max-w-6xl mx-auto px-2 sm:px-8 flex flex-col gap-4">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <UploadPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to={token ? "/" : "/login"} replace />} />
          </Routes>
        </div>
      </main>
      <footer className="glass w-full border-t border-dark-800 dark:bg-backdrop dark:bg-opacity-50 shadow-t-xl">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-5 text-xs text-slate-400 font-medium">
          <p>© {new Date().getFullYear()} AI Resume Screening System</p>
          <p>Secure · Scalable · Insightful</p>
        </div>
      </footer>
    </div>
  );
}

