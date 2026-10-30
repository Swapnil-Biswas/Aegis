import React, { useEffect, useState } from "react";
import { getBenchmarks } from "../api";
import type { BenchmarkResponse, OperatingMode } from "../types";
import {
  Award,
  RefreshCw,
  AlertOctagon,
  Sliders,
  Layers,
} from "lucide-react";

interface BenchmarkDashboardProps {
  mode: OperatingMode;
}

export const BenchmarkDashboard: React.FC<BenchmarkDashboardProps> = ({ mode }) => {
  const [data, setData] = useState<BenchmarkResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBenchmarks = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getBenchmarks(mode);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load benchmark telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmarks();
  }, [mode]);

  if (loading) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-12 text-center shadow-xl">
        <RefreshCw className="w-8 h-8 text-blue-400 animate-spin mx-auto mb-3" />
        <p className="text-sm text-gray-300 font-medium">
          Executing Scientific Forensic Validation Suite...
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Evaluating across multi-model holdouts and stratified length slices
        </p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-8 text-center shadow-xl">
        <AlertOctagon className="w-8 h-8 text-red-400 mx-auto mb-3" />
        <p className="text-sm text-red-400 font-medium">{error || "No data available."}</p>
        <button
          onClick={fetchBenchmarks}
          className="mt-4 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-xs"
        >
          Retry Benchmark Run
        </button>
      </div>
    );
  }

  const m = data.overall_metrics;
  const cm = m.confusion_matrix;

  return (
    <div className="space-y-6">
      {/* Title & Controls */}
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="w-6 h-6 text-yellow-400" />
            AEGIS Empirical Scientific Validation &amp; Evaluation Dashboard
          </h2>
          <p className="text-xs text-gray-400">
            Live run over the small bundled sample set. Held-out metrics on public MAGE/RAID data are in docs/FORENSIC_VALIDATION.md.
          </p>
        </div>

        <button
          onClick={fetchBenchmarks}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs text-gray-200 border border-gray-700"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Re-run Suite
        </button>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">AUROC</span>
          <span className="text-2xl font-bold font-mono text-blue-400 mt-1 block">
            {(m.auroc * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-gray-400">Target &gt; 95%</span>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">AUPRC</span>
          <span className="text-2xl font-bold font-mono text-purple-400 mt-1 block">
            {(m.auprc * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-gray-400">Area Under PR</span>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Precision</span>
          <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
            {(m.precision * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-gray-400">AI Positives Accuracy</span>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">False Positive Rate</span>
          <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
            {(m.false_positive_rate * 100).toFixed(2)}%
          </span>
          <span className="text-[10px] text-gray-400">Target &lt; 2.0%</span>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">ECE (Calibration)</span>
          <span className="text-2xl font-bold font-mono text-amber-400 mt-1 block">
            {(m.expected_calibration_error * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-gray-400">Expected Calib Error</span>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Brier Score</span>
          <span className="text-2xl font-bold font-mono text-cyan-400 mt-1 block">
            {m.brier_score.toFixed(3)}
          </span>
          <span className="text-[10px] text-gray-400">Lower is better</span>
        </div>
      </div>

      {/* Confusion Matrix & Length Slice Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Card */}
        <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-400" />
            Confusion Matrix (Evaluated at Decision Threshold {m.threshold.toFixed(2)})
          </h3>

          <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
            <div className="bg-emerald-950/40 border border-emerald-500/30 rounded-xl p-4 text-center">
              <span className="text-[10px] text-emerald-400 uppercase block font-semibold">
                True Negatives (Human)
              </span>
              <span className="text-3xl font-bold font-mono text-emerald-300 mt-1 block">
                {cm.true_negatives}
              </span>
              <span className="text-[10px] text-gray-400">Correct Human Attribution</span>
            </div>

            <div className="bg-red-950/40 border border-red-500/30 rounded-xl p-4 text-center">
              <span className="text-[10px] text-red-400 uppercase block font-semibold">
                False Positives
              </span>
              <span className="text-3xl font-bold font-mono text-red-300 mt-1 block">
                {cm.false_positives}
              </span>
              <span className="text-[10px] text-gray-400">Human flagged as AI</span>
            </div>

            <div className="bg-yellow-950/40 border border-yellow-500/30 rounded-xl p-4 text-center">
              <span className="text-[10px] text-yellow-400 uppercase block font-semibold">
                False Negatives
              </span>
              <span className="text-3xl font-bold font-mono text-yellow-300 mt-1 block">
                {cm.false_negatives}
              </span>
              <span className="text-[10px] text-gray-400">AI missed as Human</span>
            </div>

            <div className="bg-purple-950/40 border border-purple-500/30 rounded-xl p-4 text-center">
              <span className="text-[10px] text-purple-400 uppercase block font-semibold">
                True Positives (AI)
              </span>
              <span className="text-3xl font-bold font-mono text-purple-300 mt-1 block">
                {cm.true_positives}
              </span>
              <span className="text-[10px] text-gray-400">Correct AI Detection</span>
            </div>
          </div>
        </div>

        {/* Text Length Stratification Slices */}
        <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            Performance Stratified by Text Length Slices
          </h3>

          <div className="space-y-3">
            {Object.entries(data.length_slice_metrics).map(([sliceKey, metrics]) => (
              <div
                key={sliceKey}
                className="bg-gray-950/60 border border-gray-800 rounded-xl p-3.5 flex items-center justify-between"
              >
                <div>
                  <span className="text-xs font-bold text-gray-200 capitalize font-mono block">
                    {sliceKey}
                  </span>
                  <span className="text-[11px] text-gray-400">
                    Samples: {metrics.sample_count} | F1: {(metrics.f1_score * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="flex items-center gap-4 text-right">
                  <div>
                    <span className="text-[10px] text-gray-400 uppercase block">AUROC</span>
                    <span className="text-sm font-bold font-mono text-blue-400">
                      {(metrics.auroc * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-400 uppercase block">FPR</span>
                    <span className="text-sm font-bold font-mono text-emerald-400">
                      {(metrics.false_positive_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dataset Sample Ledger */}
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-white mb-4">
          Curated Evaluation Benchmark Ledger ({data.sample_results.length} Samples)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900 text-gray-400 border-b border-gray-800 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-2.5 px-3">Sample ID</th>
                <th className="py-2.5 px-3">Genre</th>
                <th className="py-2.5 px-3">Model Family</th>
                <th className="py-2.5 px-3">Words</th>
                <th className="py-2.5 px-3">Ground Truth</th>
                <th className="py-2.5 px-3">Calibrated p(AI)</th>
                <th className="py-2.5 px-3">Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-mono">
              {data.sample_results.map((s) => (
                <tr key={s.id} className="hover:bg-gray-900/40">
                  <td className="py-2.5 px-3 font-semibold text-gray-200">{s.id}</td>
                  <td className="py-2.5 px-3 text-gray-400 capitalize">{s.genre}</td>
                  <td className="py-2.5 px-3 text-blue-400">{s.model_family}</td>
                  <td className="py-2.5 px-3 text-gray-400">{s.word_count}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        s.ground_truth_is_ai === 1
                          ? "bg-red-500/20 text-red-300"
                          : "bg-emerald-500/20 text-emerald-300"
                      }`}
                    >
                      {s.ground_truth_is_ai === 1 ? "AI GENERATED" : "HUMAN"}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-bold text-white">
                    {(s.calibrated_ai_prob * 100).toFixed(1)}%
                  </td>
                  <td className="py-2.5 px-3 text-[11px] text-gray-300">{s.verdict}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
