import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { TextInputArea } from "./components/TextInputArea";
import { VerdictBanner } from "./components/VerdictBanner";
import { PassageHeatmap } from "./components/PassageHeatmap";
import { ModuleBreakdown } from "./components/ModuleBreakdown";
import { AdversarialStressView } from "./components/AdversarialStressView";
import { ResearchDiagnosticsView } from "./components/ResearchDiagnosticsView";
import { ForensicReportModal } from "./components/ForensicReportModal";
import { BenchmarkDashboard } from "./components/BenchmarkDashboard";
import {
  analyzeText,
  analyzeFile,
  getSystemHealth,
} from "./api";
import type {
  AnalysisResponse,
  OperatingMode,
  SystemHealth,
} from "./types";
import { FileText, Sparkles, AlertCircle } from "lucide-react";

export const App: React.FC = () => {
  const [text, setText] = useState<string>("");
  const [mode, setMode] = useState<OperatingMode>("balanced");
  const [researchMode, setResearchMode] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"analyze" | "benchmarks">("analyze");
  
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);

  // Fetch system health on load
  useEffect(() => {
    getSystemHealth()
      .then(setHealth)
      .catch((err) => console.warn("Backend not reached yet:", err.message));
  }, []);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeText(text, mode, researchMode);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Forensic analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeFile(file, mode, researchMode);
      setResult(data);
      // Populate text area with excerpt if raw text is in report
      if (data.forensic_report?.passage_level_findings?.length > 0) {
        setText(data.passage_evaluations.map((p) => p.text).join("\n\n"));
      }
    } catch (err: any) {
      setError(err.message || "File parsing failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-gray-100 flex flex-col font-sans">
      {/* Navigation Header */}
      <Header
        mode={mode}
        setMode={setMode}
        researchMode={researchMode}
        setResearchMode={setResearchMode}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {activeTab === "benchmarks" ? (
          <BenchmarkDashboard mode={mode} />
        ) : (
          <>
            {/* Input & File Upload Area */}
            <TextInputArea
              text={text}
              setText={setText}
              onAnalyze={handleAnalyze}
              onFileUpload={handleFileUpload}
              loading={loading}
            />

            {/* Analysis Results View */}
            {result && (
              <div className="space-y-6 animate-fadeIn">
                {/* Verdict Banner */}
                <VerdictBanner
                  verdict={result.verdict}
                  likelihood={result.calibrated_ai_likelihood}
                  confidence={result.confidence}
                  interval={result.uncertainty_interval}
                  disagreement={result.inter_module_disagreement}
                  notes={result.forensic_notes}
                />

                {/* Audit Action Bar */}
                <div className="flex items-center justify-between bg-gray-900/60 border border-gray-800 rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <span>
                      Forensic decomposition complete. {result.passage_count} semantic passages mapped.
                    </span>
                  </div>

                  <button
                    onClick={() => setShowReportModal(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs font-medium transition"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    Inspect Formal Audit Report
                  </button>
                </div>

                {/* Sliding-Window Passage Heatmap */}
                {result.passage_evaluations && result.passage_evaluations.length > 0 && (
                  <PassageHeatmap
                    passages={result.passage_evaluations}
                  />
                )}

                {/* Independent Analytical Layer Breakdown */}
                {result.module_contributions && (
                  <ModuleBreakdown
                    contributions={result.module_contributions}
                    contradictions={result.contradictory_signals}
                  />
                )}

                {/* Adversarial Stress-Testing Harness (Module G) */}
                <AdversarialStressView currentText={text} mode={mode} />

                {/* Research Mode Diagnostic Feature Matrix */}
                {researchMode && result.research_diagnostics && (
                  <ResearchDiagnosticsView diagnostics={result.research_diagnostics} />
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Forensic Report Modal */}
      {showReportModal && result && (
        <ForensicReportModal
          report={result.forensic_report}
          onClose={() => setShowReportModal(false)}
        />
      )}

      {/* Scientific Footer */}
      <footer className="border-t border-gray-800/80 bg-[#070b13] py-6 px-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>
            PROJECT AEGIS &copy; 2026. Advanced Multi-Layer Forensic AI Detection &amp; Attribution Architecture.
          </p>
          <div className="flex items-center gap-4 text-gray-400">
            <span>Calibrated Bayesian Stacking</span>
            <span>•</span>
            <span>Zero Fabricated Evidence</span>
            <span>•</span>
            <span>Passage Discontinuity Slicing</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
