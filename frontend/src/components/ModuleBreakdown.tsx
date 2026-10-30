import React from "react";
import type { ModuleContribution } from "../types";
import {
  BarChart2,
  Fingerprint,
  Cpu,
  GitCommit,
  Sparkles,
  Split,
  AlertCircle,
} from "lucide-react";

interface ModuleBreakdownProps {
  contributions: Record<string, ModuleContribution>;
  contradictions: string[];
}

export const ModuleBreakdown: React.FC<ModuleBreakdownProps> = ({
  contributions,
  contradictions,
}) => {
  const getModuleIcon = (key: string) => {
    switch (key) {
      case "statistical_linguistics":
        return <BarChart2 className="w-5 h-5 text-blue-400" />;
      case "stylometric_fingerprinting":
        return <Fingerprint className="w-5 h-5 text-emerald-400" />;
      case "neural_classifier":
        return <Cpu className="w-5 h-5 text-purple-400" />;
      case "semantic_discourse":
        return <GitCommit className="w-5 h-5 text-amber-400" />;
      case "pattern_analysis":
        return <Sparkles className="w-5 h-5 text-pink-400" />;
      case "discontinuity_analysis":
        return <Split className="w-5 h-5 text-cyan-400" />;
      default:
        return <BarChart2 className="w-5 h-5 text-gray-400" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return "text-red-400";
    if (score <= 0.3) return "text-emerald-400";
    return "text-yellow-400";
  };

  const getBarColor = (score: number) => {
    if (score >= 0.7) return "bg-red-500";
    if (score <= 0.3) return "bg-emerald-500";
    return "bg-yellow-500";
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">
            Multi-Layer Analytical Contributions
          </h3>
          <p className="text-xs text-gray-400">
            Independent evaluations across statistical, stylometric, neural, semantic, rhetorical, and boundary dimensions.
          </p>
        </div>
      </div>

      {/* Contradictory Evidence Alert Callout (Section 14 Rule 8: Never hide contradictory outputs) */}
      {contradictions.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200">
          <div className="flex items-center gap-2 mb-1.5 font-semibold text-xs text-amber-300">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            Contradictory Forensic Signals Detected
          </div>
          <ul className="list-disc list-inside text-xs text-amber-200/90 space-y-1">
            {contradictions.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 6 Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(contributions).map(([key, mod]) => (
          <div
            key={key}
            className="bg-gray-950/60 border border-gray-800 rounded-xl p-4 flex flex-col justify-between hover:border-gray-700 transition"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-gray-900 border border-gray-800">
                    {getModuleIcon(key)}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white leading-tight">
                      {mod.display_name}
                    </h4>
                    <span className="text-[10px] text-gray-400">
                      Ensemble Weight: {mod.weight_applied.toFixed(2)}x
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`text-base font-bold font-mono ${getScoreColor(
                      mod.score
                    )}`}
                  >
                    {(mod.score * 100).toFixed(0)}%
                  </span>
                  <span className="text-[10px] text-gray-400 block">
                    conf: {(mod.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full ${getBarColor(mod.score)}`}
                  style={{ width: `${Math.min(100, Math.max(0, mod.score * 100))}%` }}
                />
              </div>

              {/* Observations */}
              <div className="space-y-1.5 mb-2">
                {mod.observations.slice(0, 2).map((obs, idx) => (
                  <p key={idx} className="text-[11px] text-gray-300 leading-relaxed">
                    • {obs}
                  </p>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
