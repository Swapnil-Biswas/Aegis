import React, { useState } from "react";
import type { PassageEvaluation } from "../types";
import { Layers } from "lucide-react";

interface PassageHeatmapProps {
  passages: PassageEvaluation[];
}

export const PassageHeatmap: React.FC<PassageHeatmapProps> = ({
  passages,
}) => {
  const [selectedPassageId, setSelectedPassageId] = useState<string | null>(
    passages.length > 0 ? passages[0].passage_id : null
  );

  const selectedPassage =
    passages.find((p) => p.passage_id === selectedPassageId) || passages[0];

  const getColorClasses = (color: string, isSelected: boolean) => {
    const ring = isSelected ? "ring-2 ring-white scale-[1.02]" : "hover:opacity-90";
    switch (color) {
      case "green":
        return `bg-emerald-950/70 border-emerald-500/50 text-emerald-200 ${ring}`;
      case "red":
        return `bg-red-950/70 border-red-500/50 text-red-200 ${ring}`;
      case "yellow":
        return `bg-yellow-950/70 border-yellow-500/50 text-yellow-200 ${ring}`;
      case "gray":
      default:
        return `bg-gray-900 border-gray-700 text-gray-400 ${ring}`;
    }
  };

  const getBadgeColor = (color: string) => {
    switch (color) {
      case "green":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      case "red":
        return "bg-red-500/20 text-red-300 border-red-500/40";
      case "yellow":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/40";
      case "gray":
      default:
        return "bg-gray-700/30 text-gray-400 border-gray-600";
    }
  };

  if (!passages || passages.length === 0) {
    return null;
  }

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-400" />
            Passage-Level Semantic Segmentation &amp; Heatmap
          </h3>
          <p className="text-xs text-gray-400">
            Overlapping semantic sliding windows (120w window, 50w stride). Click any passage to inspect localized evidence.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px] bg-gray-900/80 px-3 py-1.5 rounded-xl border border-gray-800 flex-wrap">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            Human-Consistent
          </span>
          <span className="flex items-center gap-1.5 text-red-400">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
            AI-Consistent
          </span>
          <span className="flex items-center gap-1.5 text-yellow-400">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500 inline-block" />
            Mixed / Uncertain
          </span>
          <span className="flex items-center gap-1.5 text-gray-400">
            <span className="w-2.5 h-2.5 rounded-full bg-gray-500 inline-block" />
            Insufficient Words
          </span>
        </div>
      </div>

      {/* Grid of Passage Micro-Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5 mb-6">
        {passages.map((p) => {
          const isSelected = p.passage_id === selectedPassageId;
          return (
            <button
              key={p.passage_id}
              onClick={() => setSelectedPassageId(p.passage_id)}
              className={`text-left p-3 rounded-xl border transition-all duration-150 ${getColorClasses(
                p.color_category,
                isSelected
              )}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-mono font-bold">
                  § {p.index + 1}
                </span>
                <span className="text-[10px] font-mono font-bold">
                  {(p.calibrated_ai_score * 100).toFixed(0)}% AI
                </span>
              </div>
              <p className="text-[11px] line-clamp-2 opacity-80 font-sans">
                {p.text}
              </p>
              <div className="mt-2 text-[9px] text-gray-400 font-mono">
                {p.word_count} words
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Passage Detailed Inspector */}
      {selectedPassage && (
        <div className="bg-gray-950/70 border border-gray-800 rounded-xl p-5 shadow-inner">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 mb-3 border-b border-gray-800">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-white font-mono">
                Passage § {selectedPassage.index + 1} Details
              </span>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full border font-bold ${getBadgeColor(
                  selectedPassage.color_category
                )}`}
              >
                {selectedPassage.classification}
              </span>
              <span className="text-xs text-gray-400">
                Words: {selectedPassage.start_word}–{selectedPassage.end_word} ({selectedPassage.word_count} words)
              </span>
              <span className="text-xs text-gray-400 font-mono">
                Chars: [{selectedPassage.start_char} : {selectedPassage.end_char}]
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[10px] uppercase tracking-wider text-gray-400 block">
                  Passage AI Likelihood
                </span>
                <span className="text-base font-bold font-mono text-white">
                  {(selectedPassage.calibrated_ai_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Full Passage Text with Highlight Styling */}
          <div className="text-sm leading-relaxed text-gray-200 bg-gray-900/50 p-4 rounded-lg border border-gray-800/80 mb-3 font-serif">
            "{selectedPassage.text}"
          </div>

          {/* Key signals and observations for this passage */}
          {selectedPassage.supporting_signals.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap text-xs text-gray-300">
              <span className="text-gray-400 font-medium">Signals:</span>
              {selectedPassage.supporting_signals.map((sig, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 text-gray-300"
                >
                  {sig}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
