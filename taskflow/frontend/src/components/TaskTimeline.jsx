import React from "react";
import StepCard from "./StepCard";

export default function TaskTimeline({ steps, currentStepId }) {
  if (!steps || steps.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 text-sm">
        No steps yet. Waiting for task to start...
      </div>
    );
  }

  const sorted = [...steps].sort(
    (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0)
  );

  return (
    <div className="space-y-0">
      {sorted.map((step, index) => (
        <div key={step.id} className="relative">
          {index < sorted.length - 1 && (
            <div className="absolute left-[22px] top-[52px] w-0.5 h-4 bg-slate-700 z-0" />
          )}
          <div className="relative z-10 pb-4">
            <StepCard
              step={step}
              isCurrent={step.id === currentStepId}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
