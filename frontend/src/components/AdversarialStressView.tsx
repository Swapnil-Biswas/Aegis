import React, { useState } from "react";
import { runStressTest } from "../api";
import type { StressTestResponse, OperatingMode } from "../types";
import { ShieldAlert, Play, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";

interface AdversarialStressViewProps {
  currentText: string;
  mode: OperatingMode;
}

export const AdversarialStressView: React.FC<AdversarialStressViewProps> = ({
  currentText,
  mode,
}) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<StressTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunTest = async () => {
    if (!currentText || currentText.trim().length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const data = await runStressTest(currentText, mode);
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute adversarial stress test.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            Adversarial Robustness &amp; Attack Simulation Harness (Module G)
          </h3>
          <p className="text-xs text-gray-400">
            Systematically subjects current text to automated synonym substitutions, clause inversions, human post-editing, and translation smoothing.
          </p>
        </div>

        <button
          onClick={handleRunTest}
          disabled={loading || !currentText.trim()}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Simulating Adversarial Perturbations...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Simulate Adversarial Attacks
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-3 mb-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
          {error}
        </div>
      )}

      {results && (
        <div className="space-y-4">
          {/* Summary metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-gray-950/60 p-3.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block">
                Original AI Likelihood
              </span>
              <span className="text-lg font-bold font-mono text-white">
                {(results.original_ai_likelihood * 100).toFixed(1)}%
              </span>
              <span className="text-[10px] text-gray-400 block mt-0.5">
                Verdict: {results.original_verdict}
              </span>
            </div>

            <div className="bg-gray-950/60 p-3.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block">
                Mean Score Drift (Δ)
              </span>
              <span
                className={`text-lg font-bold font-mono ${
                  results.mean_adversarial_drift < 0.10
                    ? "text-emerald-400"
                    : "text-amber-400"
                }`}
              >
                {(results.mean_adversarial_drift * 100).toFixed(2)}%
              </span>
              <span className="text-[10px] text-gray-400 block mt-0.5">
                Target Degradation &lt; 15%
              </span>
            </div>

            <div className="bg-gray-950/60 p-3.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block">
                Robustness Rating
              </span>
              <span className="text-sm font-semibold text-gray-200 mt-1 block">
                {results.robustness_summary}
              </span>
            </div>
          </div>

          {/* Individual Perturbation Breakdown */}
          <div className="space-y-2.5">
            {results.perturbation_evaluations.map((item, idx) => (
              <div
                key={idx}
                className="bg-gray-950/50 border border-gray-800/80 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
              >
                <div className="max-w-xl">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-gray-200 capitalize font-mono">
                      {item.attack_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700">
                      Drift: {(item.score_drift * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-1.5">{item.description}</p>
                  <p className="text-[11px] text-gray-400 italic font-serif">
                    Excerpt: "{item.perturbed_excerpt}"
                  </p>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-xs text-gray-400 block">
                    Perturbed Score:{" "}
                    <strong className="text-white font-mono">
                      {(item.perturbed_score * 100).toFixed(1)}%
                    </strong>
                  </span>
                  <span
                    className={`text-[11px] font-medium block mt-1 ${
                      item.original_verdict === item.perturbed_verdict
                        ? "text-emerald-400"
                        : "text-amber-400"
                    }`}
                  >
                    {item.original_verdict === item.perturbed_verdict ? (
                      <span className="flex items-center gap-1 justify-end">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        Verdict Maintained
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 justify-end">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        Verdict Shifted ({item.perturbed_verdict})
                      </span>
                    )}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
