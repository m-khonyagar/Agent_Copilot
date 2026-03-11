import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";

export default function GoalInput({ onSubmit, isLoading }) {
  const [goal, setGoal] = useState("");
  const textareaRef = useRef(null);
  const maxChars = 1000;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [goal]);

  const handleSubmit = () => {
    const trimmed = goal.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed);
    setGoal("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const remaining = maxChars - goal.length;

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 shadow-xl">
      <textarea
        ref={textareaRef}
        value={goal}
        onChange={(e) => e.target.value.length <= maxChars && setGoal(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Enter your goal... e.g., 'Create a Python script that fetches weather data and saves to CSV'"
        className="w-full bg-transparent text-slate-100 placeholder-slate-500 resize-none outline-none text-sm leading-relaxed min-h-[80px]"
        rows={3}
        disabled={isLoading}
      />
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-700">
        <div className="flex items-center gap-3">
          <span
            className={`text-xs ${
              remaining < 100 ? "text-amber-400" : "text-slate-500"
            }`}
          >
            {remaining} chars remaining
          </span>
          <span className="text-xs text-slate-600">Ctrl+Enter to submit</span>
        </div>
        <button
          onClick={handleSubmit}
          disabled={!goal.trim() || isLoading}
          className="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition-all disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Generate Plan
            </>
          )}
        </button>
      </div>
    </div>
  );
}
