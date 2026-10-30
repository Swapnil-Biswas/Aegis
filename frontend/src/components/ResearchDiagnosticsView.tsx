import React, { useState } from "react";
import { FlaskConical, ChevronDown, ChevronRight, Copy, Check } from "lucide-react";

interface ResearchDiagnosticsViewProps {
  diagnostics: {
    all_extracted_features: Record<string, Record<string, number>>;
    uncalibrated_raw_scores: Record<string, number>;
    detector_confidences: Record<string, number>;
  };
}

export const ResearchDiagnosticsView: React.FC<ResearchDiagnosticsViewProps> = ({
  diagnostics,
}) => {
  const [copied, setCopied] = useState(false);
  const [openModules, setOpenModules] = useState<Record<string, boolean>>({
    statistical_linguistics: true,
  });

  const toggleModule = (mod: string) => {
    setOpenModules((prev) => ({ ...prev, [mod]: !prev[mod] }));
  };

  const copyFeaturesJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(diagnostics, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#111827] border border-purple-500/30 rounded-2xl p-6 shadow-xl relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-purple-300 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-purple-400" />
            Research Mode: Deep Empirical Feature Extraction Matrix
          </h3>
          <p className="text-xs text-gray-400">
            Raw high-dimensional mathematical distributions, uncalibrated logit spaces, and linguistic vector internals.
          </p>
        </div>

        <button
          onClick={copyFeaturesJSON}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-mono transition"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied JSON
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" /> Copy Feature Matrix
            </>
          )}
        </button>
      </div>

      {/* Uncalibrated Raw vs Calibrated Comparison Table */}
      <div className="mb-6 bg-gray-950/60 rounded-xl border border-gray-800 p-4">
        <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-2 font-mono">
          Module Uncalibrated Raw Scores &amp; Latent Confidences
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          {Object.entries(diagnostics.uncalibrated_raw_scores).map(([mod, raw]) => (
            <div key={mod} className="bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
              <span className="text-[10px] text-gray-400 block truncate" title={mod}>
                {mod.replace(/_/g, " ")}
              </span>
              <span className="text-xs font-bold font-mono text-purple-300 mt-0.5 block">
                raw: {raw.toFixed(3)}
              </span>
              <span className="text-[10px] text-gray-400 font-mono block">
                conf: {diagnostics.detector_confidences[mod]?.toFixed(2) || "N/A"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Accordion Feature Matrix */}
      <div className="space-y-3">
        {Object.entries(diagnostics.all_extracted_features).map(([modKey, featMap]) => {
          const isOpen = !!openModules[modKey];
          return (
            <div
              key={modKey}
              className="bg-gray-950/40 border border-gray-800/80 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => toggleModule(modKey)}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-900/40 transition"
              >
                <div className="flex items-center gap-2">
                  {isOpen ? (
                    <ChevronDown className="w-4 h-4 text-purple-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  )}
                  <span className="text-xs font-bold text-gray-200 capitalize font-mono">
                    {modKey.replace(/_/g, " ")} Features ({Object.keys(featMap).length})
                  </span>
                </div>
              </button>

              {isOpen && (
                <div className="p-4 pt-1 border-t border-gray-800/60 bg-gray-950/70">
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-xs font-mono">
                    {Object.entries(featMap).map(([param, val]) => (
                      <div
                        key={param}
                        className="p-2 rounded bg-gray-900/40 border border-gray-800/60 flex items-center justify-between"
                      >
                        <span className="text-gray-400 text-[11px] truncate mr-2" title={param}>
                          {param}:
                        </span>
                        <span className="text-purple-300 font-bold shrink-0">
                          {typeof val === "number" ? val.toFixed(4) : val}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

