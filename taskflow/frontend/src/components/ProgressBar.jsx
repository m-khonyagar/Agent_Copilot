import React from "react";

export default function ProgressBar({ progress, label }) {
  const clamped = Math.min(100, Math.max(0, progress || 0));

  return (
    <div className="space-y-1.5">
      {(label || clamped !== undefined) && (
        <div className="flex justify-between items-center">
          {label && (
            <span className="text-xs text-slate-400 font-medium">{label}</span>
          )}
          <span className="text-xs text-slate-400 ml-auto">{clamped}%</span>
        </div>
      )}
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-600 to-cyan-500 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${clamped}%` }}
        >
          {clamped > 0 && clamped < 100 && (
            <div className="h-full w-full bg-white/20 animate-pulse rounded-full" />
          )}
        </div>
      </div>
    </div>
  );
}
