import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import TaskTimeline from "../components/TaskTimeline";
import FileBrowser from "../components/FileBrowser";
import ProgressBar from "../components/ProgressBar";
import { tasksApi, createWebSocket } from "../api";
import {
  ArrowLeft,
  XCircle,
  Wifi,
  WifiOff,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Terminal,
} from "lucide-react";

const STATUS_LABEL = {
  running: "Running",
  completed: "Completed",
  failed: "Failed",
  pending: "Pending",
  cancelled: "Cancelled",
};

const STATUS_COLOR = {
  running: "text-blue-400",
  completed: "text-emerald-400",
  failed: "text-red-400",
  pending: "text-slate-400",
  cancelled: "text-amber-400",
};

function computeProgress(task) {
  if (!task) return 0;
  if (task.status === "completed") return 100;
  if (task.status === "failed" || task.status === "cancelled") return 100;
  const steps = task.steps || [];
  if (steps.length === 0) return task.status === "running" ? 10 : 0;
  const done = steps.filter(
    (s) => s.status === "completed" || s.status === "failed"
  ).length;
  return Math.round((done / steps.length) * 100);
}

function getCurrentStep(steps) {
  if (!steps) return null;
  return steps.find((s) => s.status === "running") || null;
}

export default function TaskView() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [output, setOutput] = useState([]);
  const [cancelling, setCancelling] = useState(false);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const outputEndRef = useRef(null);
  const mountedRef = useRef(true);
  const taskStatusRef = useRef(null);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchTask = useCallback(async () => {
    try {
      const res = await tasksApi.getById(taskId);
      if (mountedRef.current) {
        setTask(res.data);
        taskStatusRef.current = res.data?.status;
      }
    } catch (err) {
      if (mountedRef.current)
        setError(err.response?.data?.detail || "Failed to load task");
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [taskId]);

  const connectWs = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    try {
      const ws = createWebSocket(taskId);
      wsRef.current = ws;

      ws.onopen = () => {
        if (mountedRef.current) setWsConnected(true);
        if (reconnectRef.current) clearTimeout(reconnectRef.current);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === "task_update" || data.task) {
            const updatedTask = data.task || data;
            setTask((prev) => ({ ...prev, ...updatedTask }));
            if (updatedTask.status) taskStatusRef.current = updatedTask.status;
          } else if (data.type === "step_update" || data.step) {
            setTask((prev) => {
              if (!prev) return prev;
              const updatedStep = data.step || data;
              const steps = (prev.steps || []).map((s) =>
                s.id === updatedStep.id ? { ...s, ...updatedStep } : s
              );
              return { ...prev, steps };
            });
          } else if (data.type === "output" || data.output) {
            setOutput((prev) => [
              ...prev.slice(-200),
              data.output || data.message || JSON.stringify(data),
            ]);
          } else if (data.type === "log" || data.message) {
            setOutput((prev) => [
              ...prev.slice(-200),
              data.message || data.output || JSON.stringify(data),
            ]);
          }
          // Re-fetch full task on significant events
          if (
            data.type === "task_completed" ||
            data.type === "task_failed" ||
            data.status === "completed" ||
            data.status === "failed"
          ) {
            fetchTask();
          }
        } catch {
          setOutput((prev) => [...prev.slice(-200), event.data]);
        }
      };

      ws.onerror = () => {
        if (mountedRef.current) setWsConnected(false);
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setWsConnected(false);
        // Reconnect after 3 seconds if task is still running
        const status = taskStatusRef.current;
        if (status === "running" || status === "pending") {
          reconnectRef.current = setTimeout(() => {
            if (mountedRef.current) connectWs();
          }, 3000);
        }
      };
    } catch {
      setWsConnected(false);
    }
  }, [taskId, fetchTask]);

  useEffect(() => {
    fetchTask();
  }, [fetchTask]);

  useEffect(() => {
    connectWs();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connectWs]);

  useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [output]);

  const handleCancel = async () => {
    setCancelling(true);
    try {
      await tasksApi.cancel(taskId);
      await fetchTask();
    } catch (err) {
      console.error("Cancel failed:", err);
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Error</h2>
        <p className="text-slate-400 mb-6">{error}</p>
        <button
          onClick={() => navigate("/")}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
        >
          Back to Home
        </button>
      </div>
    );
  }

  const steps = task?.steps || [];
  const currentStep = getCurrentStep(steps);
  const progress = computeProgress(task);
  const isActive = task?.status === "running" || task?.status === "pending";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-8 gap-4 flex-wrap">
        <div className="flex items-start gap-4">
          <button
            onClick={() => navigate("/")}
            className="mt-1 p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white leading-tight max-w-2xl">
              {task?.goal || task?.name || "Task"}
            </h1>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              <span className={`text-sm font-medium flex items-center gap-1.5 ${STATUS_COLOR[task?.status] || "text-slate-400"}`}>
                {task?.status === "running" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                {task?.status === "completed" && <CheckCircle2 className="w-3.5 h-3.5" />}
                {task?.status === "failed" && <XCircle className="w-3.5 h-3.5" />}
                {STATUS_LABEL[task?.status] || task?.status}
              </span>
              <span
                className={`flex items-center gap-1 text-xs ${
                  wsConnected ? "text-emerald-400" : "text-slate-500"
                }`}
              >
                {wsConnected ? (
                  <Wifi className="w-3.5 h-3.5" />
                ) : (
                  <WifiOff className="w-3.5 h-3.5" />
                )}
                {wsConnected ? "Live" : "Offline"}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {isActive && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {cancelling ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left Panel */}
        <div className="lg:col-span-2 space-y-5">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
            <h2 className="text-sm font-semibold text-slate-300 mb-4">
              Progress
            </h2>
            <ProgressBar
              progress={progress}
              label={`${steps.filter((s) => s.status === "completed").length} / ${steps.length} steps`}
            />
            {currentStep && (
              <p className="mt-3 text-xs text-slate-400">
                Currently:{" "}
                <span className="text-blue-400">{currentStep.name}</span>
              </p>
            )}
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
            <h2 className="text-sm font-semibold text-slate-300 mb-4">
              Steps
            </h2>
            <TaskTimeline steps={steps} currentStepId={currentStep?.id} />
          </div>
        </div>

        {/* Right Panel */}
        <div className="lg:col-span-3 space-y-5">
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700">
              <Terminal className="w-4 h-4 text-slate-400" />
              <h2 className="text-sm font-semibold text-slate-300">
                Live Output
              </h2>
              {wsConnected && (
                <span className="ml-auto flex items-center gap-1 text-xs text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live
                </span>
              )}
            </div>
            <div className="p-4 h-72 overflow-y-auto bg-slate-900/50 font-mono text-xs">
              {output.length === 0 ? (
                <div className="flex items-center justify-center h-full text-slate-600">
                  Waiting for output...
                </div>
              ) : (
                <div className="space-y-0.5">
                  {output.map((line, i) => (
                    <div key={i} className="text-slate-300 leading-relaxed">
                      <span className="text-slate-600 mr-2 select-none">›</span>
                      {line}
                    </div>
                  ))}
                  <div ref={outputEndRef} />
                </div>
              )}
            </div>
          </div>

          <FileBrowser taskId={taskId} />
        </div>
      </div>
    </div>
  );
}
