import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { tasksApi } from "../api";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Circle,
  Eye,
  Trash2,
  Search,
  Clock,
  AlertCircle,
  History as HistoryIcon,
} from "lucide-react";

const STATUS_OPTIONS = ["all", "running", "completed", "failed", "pending", "cancelled"];

const statusConfig = {
  completed: {
    icon: CheckCircle2,
    iconClass: "text-emerald-400",
    badge: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
    label: "Completed",
  },
  running: {
    icon: Loader2,
    iconClass: "text-blue-400 animate-spin",
    badge: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
    label: "Running",
  },
  failed: {
    icon: XCircle,
    iconClass: "text-red-400",
    badge: "bg-red-500/20 text-red-300 border border-red-500/30",
    label: "Failed",
  },
  pending: {
    icon: Circle,
    iconClass: "text-slate-500",
    badge: "bg-slate-700 text-slate-400 border border-slate-600",
    label: "Pending",
  },
  cancelled: {
    icon: XCircle,
    iconClass: "text-amber-400",
    badge: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
    label: "Cancelled",
  },
};

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function History() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
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
      setError("Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this task?")) return;
    setDeletingId(id);
    try {
      await tasksApi.delete(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch {
      alert("Failed to delete task");
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = tasks.filter((t) => {
    const matchStatus = filter === "all" || t.status === filter;
    const goal = (t.goal || t.name || "").toLowerCase();
    const matchSearch = !search || goal.includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center gap-3 mb-8">
        <HistoryIcon className="w-6 h-6 text-blue-400" />
        <h1 className="text-2xl font-bold text-white">Task History</h1>
        {!loading && (
          <span className="ml-auto text-sm text-slate-500">
            {filtered.length} task{filtered.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {STATUS_OPTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-2 rounded-lg text-xs font-medium capitalize transition-colors ${
                filter === s
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 mb-6">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-7 h-7 animate-spin text-slate-500" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 rounded-xl border border-dashed border-slate-700">
          <div className="text-4xl mb-3">📭</div>
          <p className="text-slate-400 font-medium">No tasks found</p>
          <p className="text-slate-600 text-sm mt-1">
            {search || filter !== "all"
              ? "Try adjusting your filters"
              : "No tasks have been created yet"}
          </p>
        </div>
      ) : (
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-5 py-3">
                  Task
                </th>
                <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3 hidden sm:table-cell">
                  Status
                </th>
                <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3 hidden md:table-cell">
                  Created
                </th>
                <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-5 py-3">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filtered.map((task) => {
                const cfg = statusConfig[task.status] || statusConfig.pending;
                const Icon = cfg.icon;
                return (
                  <tr
                    key={task.id}
                    className="hover:bg-slate-700/30 transition-colors cursor-pointer"
                    onClick={() => navigate(`/task/${task.id}`)}
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <Icon className={`w-4 h-4 shrink-0 ${cfg.iconClass}`} />
                        <span className="text-sm text-slate-200 font-medium line-clamp-1">
                          {task.goal || task.name || "Untitled"}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 hidden sm:table-cell">
                      <span
                        className={`inline-block text-xs px-2.5 py-1 rounded-full font-medium ${cfg.badge}`}
                      >
                        {cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-4 hidden md:table-cell">
                      <span className="text-xs text-slate-500 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        {formatDate(task.created_at || task.createdAt)}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div
                        className="flex items-center justify-end gap-2"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={() => navigate(`/task/${task.id}`)}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white rounded-md text-xs font-medium transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View
                        </button>
                        <button
                          onClick={(e) => handleDelete(task.id, e)}
                          disabled={deletingId === task.id}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 border border-red-500/20 rounded-md text-xs font-medium transition-colors disabled:opacity-50"
                        >
                          {deletingId === task.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="w-3.5 h-3.5" />
                          )}
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
