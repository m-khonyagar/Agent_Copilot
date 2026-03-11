import React from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import TaskView from "./pages/TaskView";
import History from "./pages/History";
import { Zap } from "lucide-react";

function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
        isActive
          ? "bg-slate-700 text-white"
          : "text-slate-400 hover:text-white hover:bg-slate-700/50"
      }`}
    >
      {children}
    </Link>
  );
}

function Header() {
  return (
    <header className="bg-slate-900 border-b border-slate-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl">
            <div className="bg-blue-600 rounded-lg p-1.5">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              TaskFlow AI
            </span>
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/history">History</NavLink>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/task/:taskId" element={<TaskView />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
