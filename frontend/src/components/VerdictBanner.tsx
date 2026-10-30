import React from "react";
import type { ClassificationVerdict } from "../types";
import {
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileX,
  Layers,
  Sparkles,
  Info,
} from "lucide-react";

interface VerdictBannerProps {
  verdict: ClassificationVerdict;
  likelihood: number;
  confidence: number;
  interval: [number, number];
  disagreement: number;
  notes: string[];
}

export const VerdictBanner: React.FC<VerdictBannerProps> = ({
  verdict,
  likelihood,
  confidence,
  interval,
  disagreement,
  notes,
}) => {
  const getVerdictConfig = () => {
    switch (verdict) {
      case "HUMAN_AUTHENTIC":
        return {
          title: "AUTHENTIC HUMAN WRITING",
          badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
          accentColor: "text-emerald-400",
          barColor: "bg-emerald-500",
          icon: <CheckCircle2 className="w-8 h-8 text-emerald-400" />,
          desc: "Observed statistical, stylometric, and neural distributions align with natural human prose.",
        };
      case "AI_GENERATED":
        return {
          title: "SYNTHETIC AI GENERATION",
          badgeColor: "bg-red-500/20 text-red-300 border-red-500/40",
          accentColor: "text-red-400",
          barColor: "bg-red-500",
          icon: <AlertTriangle className="w-8 h-8 text-red-400" />,
          desc: "Multiple independent analytical layers demonstrate synthetic model generation hallmarks.",
        };
      case "AI_ASSISTED_EDITED":
        return {
          title: "AI-GENERATED (HUMAN EDITED)",
          badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
          accentColor: "text-amber-400",
          barColor: "bg-amber-500",
          icon: <Sparkles className="w-8 h-8 text-amber-400" />,
          desc: "Synthetic linguistic backbone detected alongside localized human revisions and contractions.",
        };
      case "HYBRID_MIXED":
        return {
          title: "COMPOSITE HYBRID WRITING",
          badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
          accentColor: "text-purple-400",
          barColor: "bg-purple-500",
          icon: <Layers className="w-8 h-8 text-purple-400" />,
          desc: "Passage-level divergence detects distinct clusters of authentic human and synthetic text.",
        };
      case "HUMAN_PARAPHRASED_BY_AI":
        return {
          title: "HUMAN PARAPHRASED BY AI",
          badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
          accentColor: "text-cyan-400",
          barColor: "bg-cyan-500",
          icon: <AlertTriangle className="w-8 h-8 text-cyan-400" />,
          desc: "Human thematic progression smoothed and restructured through an automated model.",
        };
      case "INSUFFICIENT_EVIDENCE":
        return {
          title: "INSUFFICIENT EVIDENCE",
          badgeColor: "bg-gray-600/20 text-gray-400 border-gray-600/40",
          accentColor: "text-gray-400",
          barColor: "bg-gray-600",
          icon: <FileX className="w-8 h-8 text-gray-400" />,
          desc: "Sample text is below the 60-word threshold required for mathematically valid confidence intervals.",
        };
      case "INCONCLUSIVE":
      default:
        return {
          title: "INCONCLUSIVE / AMBIGUOUS",
          badgeColor: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40",
          accentColor: "text-yellow-400",
          barColor: "bg-yellow-500",
          icon: <HelpCircle className="w-8 h-8 text-yellow-400" />,
          desc: "Analytical layers exhibit discordance or probability falls within the ambiguous boundary zone.",
        };
    }
  };

  const config = getVerdictConfig();

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        {/* Left: Icon and Title */}
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-2xl bg-gray-900 border border-gray-800 shadow-inner">
            {config.icon}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span
                className={`text-xs font-bold tracking-wider px-3 py-1 rounded-full border ${config.badgeColor}`}
              >
                {config.title}
              </span>
              <span className="text-xs text-gray-400">
                Confidence:{" "}
                <strong className="text-gray-200">
                  {(confidence * 100).toFixed(1)}%
                </strong>
              </span>
              {disagreement > 0.15 && (
                <span className="text-[11px] px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                  Inter-Module Disagreement: {(disagreement * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p className="text-sm text-gray-300 max-w-2xl">{config.desc}</p>
            {notes.length > 0 && (
              <p className="text-xs text-gray-400 mt-1 italic">{notes[0]}</p>
            )}
          </div>
        </div>

        {/* Right: Likelihood and Uncertainty Gauges */}
        <div className="w-full lg:w-80 bg-gray-950/60 p-4 rounded-xl border border-gray-800/80">
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Calibrated AI Likelihood
            </span>
            <span className={`text-2xl font-bold font-mono ${config.accentColor}`}>
              {(likelihood * 100).toFixed(1)}%
            </span>
          </div>

          {/* Calibrated Bar */}
          <div className="w-full bg-gray-800 h-2.5 rounded-full overflow-hidden relative">
            <div
              className={`h-full transition-all duration-700 ${config.barColor}`}
              style={{ width: `${Math.min(100, Math.max(0, likelihood * 100))}%` }}
            />
          </div>

          {/* Uncertainty Range */}
          <div className="flex items-center justify-between mt-2 text-[11px] text-gray-400">
            <span>
              95% Posterior Interval:{" "}
              <strong className="text-gray-300 font-mono">
                [{(interval[0] * 100).toFixed(1)}% – {(interval[1] * 100).toFixed(1)}%]
              </strong>
            </span>
          </div>
        </div>
      </div>

      {/* Non-negotiable Scientific Disclaimer */}
      <div className="mt-4 pt-3 border-t border-gray-800/60 flex items-center gap-2 text-[11px] text-gray-400">
        <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />
        <span>
          <strong>Scientific Integrity Notice:</strong> AEGIS scores represent mathematical probability estimates based on empirical corpus statistics. They do not constitute an accusation of misconduct or absolute proof.
        </span>
      </div>
    </div>
  );
};
