import React from "react";
import type { ForensicReport } from "../types";
import { X, Download, FileText, AlertTriangle } from "lucide-react";

interface ForensicReportModalProps {
  report: ForensicReport;
  onClose: () => void;
}

export const ForensicReportModal: React.FC<ForensicReportModalProps> = ({
  report,
  onClose,
}) => {
  const downloadJSON = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `AEGIS_Forensic_Report_${report.report_id.slice(0, 8)}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case "FACT":
        return "bg-blue-500/20 text-blue-300 border-blue-500/30";
      case "STATISTICAL_CORRELATION":
        return "bg-purple-500/20 text-purple-300 border-purple-500/30";
      case "MODEL_PREDICTION":
        return "bg-amber-500/20 text-amber-300 border-amber-500/30";
      case "LIMITATION":
      default:
        return "bg-gray-700/30 text-gray-400 border-gray-600";
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/60">
          <div className="flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-base font-bold text-white">
                Official AEGIS Forensic Audit Report
              </h3>
              <p className="text-xs text-gray-400 font-mono">
                Report ID: {report.report_id}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={downloadJSON}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition"
            >
              <Download className="w-3.5 h-3.5" /> Export JSON
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-gray-300">
          {/* Executive Overview */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-gray-950/60 p-4 rounded-xl border border-gray-800">
            <div>
              <span className="text-[10px] text-gray-400 uppercase block font-semibold">
                Attribution Verdict
              </span>
              <span className="text-sm font-bold text-white mt-1 block">
                {report.verdict}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-gray-400 uppercase block font-semibold">
                Calibrated p(AI)
              </span>
              <span className="text-sm font-bold font-mono text-blue-400 mt-1 block">
                {(report.calibrated_ai_likelihood * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-[10px] text-gray-400 uppercase block font-semibold">
                Reliability Tier
              </span>
              <span className="text-sm font-bold text-emerald-400 mt-1 block">
                {report.reliability_tier}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-gray-400 uppercase block font-semibold">
                Document Size
              </span>
              <span className="text-sm font-bold text-gray-300 mt-1 block">
                {report.document_summary.total_words} words ({report.document_summary.total_sentences} sents)
              </span>
            </div>
          </div>

          {/* Categorized Forensic Observations */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">
              Audited Empirical Observations
            </h4>
            <div className="space-y-2">
              {report.observations.map((obs, idx) => (
                <div
                  key={idx}
                  className="bg-gray-950/40 border border-gray-800/80 rounded-xl p-3 flex items-start gap-3"
                >
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded font-mono uppercase font-bold tracking-wider shrink-0 border ${getCategoryBadge(
                      obs.category
                    )}`}
                  >
                    {obs.category}
                  </span>
                  <div>
                    <span className="text-gray-400 font-semibold mr-1.5">
                      [{obs.dimension}]:
                    </span>
                    <span className="text-gray-200">{obs.statement}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Contradictory Evidence Section */}
          {report.contradictory_evidence.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Isolated Contradictory Signals
              </h4>
              <ul className="list-disc list-inside bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 text-amber-200 space-y-1">
                {report.contradictory_evidence.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Epistemic Limitations */}
          <div>
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
              Epistemic Boundaries &amp; Known Limitations
            </h4>
            <ul className="list-disc list-inside bg-gray-900/40 border border-gray-800 rounded-xl p-3 text-gray-400 space-y-1 text-[11px]">
              {report.epistemic_limitations.map((lim, i) => (
                <li key={i}>{lim}</li>
              ))}
            </ul>
          </div>

          {/* Legal Disclaimer */}
          <div className="p-3 bg-gray-950 rounded-xl border border-gray-800 text-[10px] text-gray-500 italic">
            {report.disclaimer}
          </div>
        </div>
      </div>
    </div>
  );
};
