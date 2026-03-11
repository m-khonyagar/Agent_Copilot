import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import GoalInput from "../components/GoalInput";
import { tasksApi } from "../api";
import {
  Zap,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Circle,
  ArrowRight,
  LayoutDashboard,
} from "lucide-react";

const statusConfig = {
  completed: {
    icon: CheckCircle2,
    class: "text-emerald-400",
    badge: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
    label: "Completed",
  },
  running: {
    icon: Loader2,
    class: "text-blue-400 animate-spin",
    badge: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
    label: "Running",
  },
  failed: {
    icon: XCircle,
    class: "text-red-400",
    badge: "bg-red-500/20 text-red-300 border border-red-500/30",
    label: "Failed",
  },
  pending: {
    icon: Circle,
    class: "text-slate-500",
    badge: "bg-slate-700 text-slate-400 border border-slate-600",
    label: "Pending",
  },
  cancelled: {
    icon: XCircle,
    class: "text-amber-400",
    badge: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
    label: "Cancelled",
  },
};

function TaskRow({ task, onClick }) {
  const cfg = statusConfig[task.status] || statusConfig.pending;
  const Icon = cfg.icon;
  const date = new Date(task.created_at || task.createdAt || Date.now());
  const relative = formatRelative(date);

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-4 p-4 rounded-lg bg-slate-800 hover:bg-slate-700/80 border border-slate-700 hover:border-slate-600 transition-all text-left group"
    >
      <Icon className={`w-5 h-5 shrink-0 ${cfg.class}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-200 font-medium truncate">
          {task.goal || task.name || "Untitled Task"}
        </p>
        <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          {relative}
        </p>
      </div>
      <span className={`text-xs px-2.5 py-1 rounded-full font-medium shrink-0 ${cfg.badge}`}>
        {cfg.label}
      </span>
      <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors shrink-0" />
    </button>
  );
}

function formatRelative(date) {
  const now = Date.now();
  const diff = now - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await tasksApi.getAll();
      const data = res.data;
      const list = Array.isArray(data) ? data : data.tasks || [];
      list.sort((a, b) => {
        const aDate = new Date(a.created_at || a.createdAt || 0);
        const bDate = new Date(b.created_at || b.createdAt || 0);
        return bDate - aDate;
      });
      setTasks(list);
    } catch {
      // Silently fail if backend not available
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleSubmit = async (goal) => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await tasksApi.create(goal);
      const task = res.data;
      const id = task.id || task.task_id;
      navigate(`/task/${id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create task. Is the backend running?");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-4">
          <div className="bg-blue-600/20 border border-blue-500/30 rounded-2xl p-4">
            <Zap className="w-10 h-10 text-blue-400" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-white mb-3">
          TaskFlow{" "}
          <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            AI
          </span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Describe your goal and let AI break it into actionable steps, execute
          them autonomously, and deliver results.
        </p>
      </div>

      {/* Goal Input */}
      <div className="mb-10">
        <GoalInput onSubmit={handleSubmit} isLoading={submitting} />
        {error && (
          <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Recent Tasks */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="flex items-center gap-2 text-slate-200 font-semibold">
            <LayoutDashboard className="w-4 h-4 text-slate-400" />
            Recent Tasks
          </h2>
          {tasks.length > 0 && (
            <button
              onClick={() => navigate("/history")}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              View all →
            </button>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-slate-500 mx-auto" />
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-16 rounded-xl border border-dashed border-slate-700">
            <div className="text-slate-600 text-4xl mb-3">✨</div>
            <p className="text-slate-400 font-medium">No tasks yet</p>
            <p className="text-slate-600 text-sm mt-1">
              Enter a goal above to get started
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.slice(0, 5).map((task) => (
              <TaskRow
                key={task.id}
                task={task}
                onClick={() => navigate(`/task/${task.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
