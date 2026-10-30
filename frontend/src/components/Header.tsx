import React from "react";
import type { OperatingMode, SystemHealth } from "../types";
import { ShieldCheck, Cpu, FlaskConical } from "lucide-react";

interface HeaderProps {
  mode: OperatingMode;
  setMode: (mode: OperatingMode) => void;
  researchMode: boolean;
  setResearchMode: (val: boolean) => void;
  activeTab: "analyze" | "benchmarks";
  setActiveTab: (tab: "analyze" | "benchmarks") => void;
  health: SystemHealth | null;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  setMode,
  researchMode,
  setResearchMode,
  activeTab,
  setActiveTab,
  health,
}) => {
  return (
    <header className="border-b border-gray-800 bg-[#0d1322] px-6 py-4 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo and System Title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-600/10 border border-blue-500/30 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.3)]">
            <ShieldCheck className="w-7 h-7 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wider text-white font-mono">
                AEGIS
              </h1>
              <span className="text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
                FORENSIC v1.0
              </span>
              {health?.cuda_available && (
                <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  <Cpu className="w-3 h-3" /> CUDA ACCELERATED
                </span>
              )}
            </div>
            <p className="text-xs text-gray-400">
              Multi-Layer AI Forensic Text Detection & Attribution System
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 bg-gray-900/80 p-1 rounded-xl border border-gray-800">
          <button
            onClick={() => setActiveTab("analyze")}
            className={`px-4 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeTab === "analyze"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-400 hover:text-white"
            }`}
          >
            Forensic Inspection
          </button>
          <button
            onClick={() => setActiveTab("benchmarks")}
            className={`px-4 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeTab === "benchmarks"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-400 hover:text-white"
            }`}
          >
            Evaluation Benchmarks
          </button>
        </div>

        {/* Operational Profile & Research Mode */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-gray-400 font-medium">Profile:</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as OperatingMode)}
              className="bg-gray-900 border border-gray-700 text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500"
            >
              <option value="high_precision">High Precision (Min FPR &lt; 1%)</option>
              <option value="balanced">Balanced (Optimal F1)</option>
              <option value="exploratory">Exploratory Screening</option>
            </select>
          </div>

          <label className="flex items-center gap-2 cursor-pointer bg-gray-900/60 px-3 py-1.5 rounded-lg border border-gray-800 hover:border-gray-700 transition">
            <FlaskConical
              className={`w-4 h-4 ${
                researchMode ? "text-purple-400" : "text-gray-500"
              }`}
            />
            <span
              className={`text-xs font-medium ${
                researchMode ? "text-purple-300" : "text-gray-400"
              }`}
            >
              Research Mode
            </span>
            <input
              type="checkbox"
              checked={researchMode}
              onChange={(e) => setResearchMode(e.target.checked)}
              className="rounded bg-gray-800 border-gray-700 text-purple-600 focus:ring-0 w-3.5 h-3.5"
            />
          </label>
        </div>
      </div>
    </header>
  );
};
