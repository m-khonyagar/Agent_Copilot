import React, { useState } from "react";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Circle,
  ChevronDown,
  ChevronUp,
  Terminal,
} from "lucide-react";

const statusConfig = {
  running: {
    icon: Loader2,
    iconClass: "text-blue-400 animate-spin",
    border: "border-blue-500/50",
    bg: "bg-blue-500/10",
    badge: "bg-blue-500/20 text-blue-300",
    label: "Running",
  },
  completed: {
    icon: CheckCircle2,
    iconClass: "text-emerald-400",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/5",
    badge: "bg-emerald-500/20 text-emerald-300",
    label: "Completed",
  },
  failed: {
    icon: XCircle,
    iconClass: "text-red-400",
    border: "border-red-500/30",
    bg: "bg-red-500/5",
    badge: "bg-red-500/20 text-red-300",
    label: "Failed",
  },
  pending: {
    icon: Circle,
    iconClass: "text-slate-500",
    border: "border-slate-700",
    bg: "",
    badge: "bg-slate-700 text-slate-400",
    label: "Pending",
  },
};

export default function StepCard({ step, isCurrent }) {
  const [expanded, setExpanded] = useState(false);
  const config = statusConfig[step.status] || statusConfig.pending;
  const Icon = config.icon;
  const hasOutput = step.output || step.error;

  return (
    <div
      className={`rounded-lg border p-4 transition-all ${config.border} ${config.bg} ${
        isCurrent ? "ring-2 ring-blue-500/40 shadow-lg shadow-blue-500/10" : ""
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 shrink-0">
          <Icon className={`w-5 h-5 ${config.iconClass}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-slate-200 truncate">
              {step.name}
            </h4>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${config.badge}`}
            >
              {config.label}
            </span>
          </div>
          {step.description && (
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              {step.description}
            </p>
          )}
          {hasOutput && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1.5 mt-2 text-xs text-slate-500 hover:text-slate-300 transition-colors"
            >
              <Terminal className="w-3.5 h-3.5" />
              {expanded ? "Hide" : "Show"} output
              {expanded ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {expanded && hasOutput && (
        <div className="mt-3 rounded-md bg-slate-900/80 border border-slate-700/50 p-3 max-h-48 overflow-y-auto">
          {step.error ? (
            <pre className="text-xs text-red-400 whitespace-pre-wrap font-mono leading-relaxed">
              {step.error}
            </pre>
          ) : (
            <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed">
              {step.output}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
