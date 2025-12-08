import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import { CloudArrowUpIcon, ChartBarIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/outline";
import UploadPage from "./pages/Upload.jsx";
import DashboardPage from "./pages/Dashboard.jsx";
import LoginPage from "./pages/Login.jsx";
import RegisterPage from "./pages/Register.jsx";

const navLinkClass = ({ isActive }) =>
  `inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
    isActive ? "bg-primary-600 text-white shadow" : "text-slate-600 hover:bg-primary-100"
  }`;

// Protected route wrapper
function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  const token = localStorage.getItem("access_token");
  
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  };

  return (
    <div className="min-h-screen">
      {token && (
        <header className="bg-white border-b border-slate-200">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-xl font-semibold text-primary-700">AI Resume Screening</h1>
              <p className="text-sm text-slate-500">
                Intelligent candidate insights for high-velocity hiring teams
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
                className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-red-100 hover:text-red-600"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
                Logout
              </button>
            </nav>
          </div>
        </header>
      )}
      <main className={token ? "mx-auto max-w-6xl px-6 py-10" : ""}>
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
      </main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 text-sm text-slate-500">
          <p>© {new Date().getFullYear()} AI-Powered Resume Screening System</p>
          <p>Secure · Scalable · Insightful</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

