import React, { useRef } from "react";
import { Upload, Trash2, Zap, ArrowRight } from "lucide-react";

interface TextInputAreaProps {
  text: string;
  setText: (val: string) => void;
  onAnalyze: () => void;
  onFileUpload: (file: File) => void;
  loading: boolean;
}

const PRESET_SAMPLES: Record<string, { label: string; text: string }> = {
  human_academic: {
    label: "Human Academic Biology Paper",
    text: "The regulation of mitochondrial dynamics is critical for cellular metabolic homeostasis in eukaryotic organisms. We investigated the interaction between mitofusin-2 (Mfn2) and optic atrophy 1 (Opa1) under induced hypoxic stress in cultured murine cortical neurons. When cells were subjected to 1% oxygen tension for six hours, total ATP concentration plummeted by 42.7% (p < 0.01), accompanied by a conspicuous fragmentation of the mitochondrial network. Intriguingly, exogenous supplementation with NAD+ precursors rescued cristae junction morphology without fully restoring baseline respiratory control ratios. These observations suggest that mitochondrial elongation and inner membrane structural preservation can operate through distinct, partially uncoupled biochemical pathways under acute energetic compromise.",
  },
  human_creative: {
    label: "Human Creative Memoir",
    text: "Old man Henderson smelled like damp wool and turpentine. He didn't speak much on Tuesdays—that was his routine, something to do with the ferry schedules or an old superstition from his tugboat years on the bay. We sat on the overturned cedar crates behind the fish-packing shed, our boots dangling over the greasy tide line. The seagulls shrieked overhead like rusty hinges. 'You've got that restless look again,' he muttered around his pipe, barely looking up from his whittling. He was carving a small, crooked pelican from a scrap of pine he'd fished out of the harbor that morning.",
  },
  ai_gpt4: {
    label: "AI GPT-4 Generated Essay",
    text: "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming traditional educational methodologies. It is important to remember that technology does not merely replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to diverse student needs. Delving into the pedagogical implications, one observes a profound synergy between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these sophisticated systems stands as a testament to the ever-evolving nature of global education.",
  },
  ai_claude_technical: {
    label: "AI Claude Technical Analysis",
    text: "Microservices architecture offers distinct advantages for large-scale distributed enterprise systems. By decoupling monolithic applications into independent deployable units, development teams can enhance modularity, facilitate continuous deployment, and improve fault isolation. However, this architectural paradigm introduces non-trivial operational complexity, particularly concerning distributed tracing, data consistency, and network latency overhead. To mitigate these challenges, organizations frequently implement service meshes, robust API gateways, and asynchronous event-driven messaging patterns. In conclusion, while microservices require rigorous governance and mature DevOps practices, their strategic deployment enables unprecedented organizational agility.",
  },
  hybrid_mixed: {
    label: "Hybrid Mixed Composite (Human + AI)",
    text: "My grandfather spent forty years restoring wooden schooners along the coast of Maine. His hands were always calloused and stained with dark Stockholm tar, and he could tell the moisture content of white oak simply by running his thumbnail along the grain. In today's fast-paced maritime landscape, modern composites play a pivotal role in revolutionizing naval architecture. It is important to remember that carbon fiber fosters a vibrant and multifaceted synergy with traditional hull design. Delving into hydrodynamic efficiency, contemporary boatbuilders utilize computational fluid dynamics to optimize laminar flow. In conclusion, the synthesis of historic craft and modern engineering stands as a testament to nautical innovation.",
  },
  short_insufficient: {
    label: "Short Sample (< 60 words: Insufficient)",
    text: "This brief introductory paragraph discusses solar cell efficiency. Silicon wafers convert incoming photon energy into electrical current through the photovoltaic effect.",
  },
};

export const TextInputArea: React.FC<TextInputAreaProps> = ({
  text,
  setText,
  onAnalyze,
  onFileUpload,
  loading,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 shadow-xl space-y-4">
      {/* Top action row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">
            Load Preset Benchmark:
          </span>
          <select
            onChange={(e) => {
              const val = e.target.value;
              if (val && PRESET_SAMPLES[val]) {
                setText(PRESET_SAMPLES[val].text);
              }
            }}
            defaultValue=""
            className="bg-gray-900 border border-gray-700 text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="" disabled>
              Select empirical benchmark sample...
            </option>
            {Object.entries(PRESET_SAMPLES).map(([k, v]) => (
              <option key={k} value={k}>
                {v.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          {/* File Upload Trigger */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.pdf,.docx,.md"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700 text-xs transition"
          >
            <Upload className="w-3.5 h-3.5 text-blue-400" />
            Upload PDF / DOCX / TXT
          </button>

          {text && (
            <button
              onClick={() => setText("")}
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-gray-800 transition"
              title="Clear Text"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Primary Textarea */}
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste investigative text or upload a document (PDF, DOCX, TXT) for multi-layer forensic analysis..."
          rows={7}
          className="w-full bg-gray-950/80 border border-gray-800 rounded-xl p-4 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 font-sans leading-relaxed resize-y transition shadow-inner"
        />

        {/* Live Counters & Minimum Indicator */}
        <div className="flex items-center justify-between text-xs text-gray-400 px-1 mt-1.5">
          <div className="flex items-center gap-3">
            <span>
              Words:{" "}
              <strong
                className={
                  wordCount < 60
                    ? "text-amber-400 font-mono"
                    : "text-gray-200 font-mono"
                }
              >
                {wordCount}
              </strong>{" "}
              {wordCount < 60 && "(Min 60 words for valid evidence)"}
            </span>
            <span>
              Characters: <strong className="text-gray-200 font-mono">{charCount}</strong>
            </span>
          </div>

          <span className="text-[11px] text-gray-500">
            Supports multi-paragraph sliding window segmentation
          </span>
        </div>
      </div>

      {/* Submit Analysis Bar */}
      <div className="flex justify-end pt-1">
        <button
          onClick={onAnalyze}
          disabled={loading || !text.trim()}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs tracking-wide shadow-lg shadow-blue-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              Running Multi-Layer Forensic Decomposition...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 fill-white" />
              Run Calibrated Forensic Analysis
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
