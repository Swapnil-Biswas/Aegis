export type OperatingMode = "high_precision" | "balanced" | "exploratory";

export type ClassificationVerdict =
  | "HUMAN_AUTHENTIC"
  | "AI_GENERATED"
  | "AI_ASSISTED_EDITED"
  | "HUMAN_PARAPHRASED_BY_AI"
  | "HYBRID_MIXED"
  | "INCONCLUSIVE"
  | "INSUFFICIENT_EVIDENCE";

export interface PassageEvaluation {
  passage_id: string;
  index: number;
  text: string;
  start_char: number;
  end_char: number;
  start_word: number;
  end_word: number;
  word_count: number;
  calibrated_ai_score: floatNumber;
  confidence: number;
  color_category: "green" | "red" | "yellow" | "gray";
  classification: string;
  supporting_signals: string[];
}

type floatNumber = number;

export interface ModuleContribution {
  display_name: string;
  score: number;
  confidence: number;
  weight_applied: number;
  observations: string[];
}

export interface ForensicObservation {
  category: "FACT" | "STATISTICAL_CORRELATION" | "MODEL_PREDICTION" | "LIMITATION";
  dimension: string;
  statement: string;
  empirical_metric?: string;
  metric_value?: number;
}

export interface ForensicReport {
  report_id: string;
  document_summary: {
    total_characters: number;
    total_words: number;
    total_sentences: number;
    total_paragraphs: number;
    total_passages: number;
    has_sufficient_evidence: boolean;
  };
  verdict: ClassificationVerdict;
  verdict_description: string;
  calibrated_ai_likelihood: number;
  confidence: number;
  confidence_interval: [number, number];
  reliability_tier: "VERY_HIGH" | "HIGH" | "MODERATE" | "LOW" | "INSUFFICIENT";
  operating_mode: string;
  observations: ForensicObservation[];
  contradictory_evidence: string[];
  passage_level_findings: Array<{
    passage_id: string;
    index: number;
    word_count: number;
    start_char: number;
    end_char: number;
    ai_score: number;
    color_category: string;
    classification: string;
    excerpt: string;
  }>;
  epistemic_limitations: string[];
  disclaimer: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  verdict: ClassificationVerdict;
  calibrated_ai_likelihood: number;
  confidence: number;
  uncertainty_interval: [number, number];
  operating_mode: OperatingMode;
  has_sufficient_evidence: boolean;
  word_count: number;
  sentence_count: number;
  passage_count: number;
  inter_module_disagreement: number;
  module_contributions: Record<string, ModuleContribution>;
  passage_evaluations: PassageEvaluation[];
  contradictory_signals: string[];
  forensic_notes: string[];
  forensic_report: ForensicReport;
  research_diagnostics?: {
    all_extracted_features: Record<string, Record<string, number>>;
    uncalibrated_raw_scores: Record<string, number>;
    detector_confidences: Record<string, number>;
    passage_breakdown_matrix: Array<{
      passage_id: string;
      index: number;
      calibrated_score: number;
      color_category: string;
      supporting_signals: string[];
    }>;
  };
}

export interface StressTestResponse {
  original_ai_likelihood: number;
  original_verdict: string;
  mean_adversarial_drift: number;
  robustness_summary: string;
  perturbation_evaluations: Array<{
    attack_type: string;
    description: string;
    perturbed_excerpt: string;
    original_score: number;
    perturbed_score: number;
    score_drift: number;
    original_verdict: string;
    perturbed_verdict: string;
  }>;
}

export interface BenchmarkMetrics {
  sample_count: number;
  threshold: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  specificity: number;
  false_positive_rate: number;
  false_negative_rate: number;
  auroc: number;
  auprc: number;
  brier_score: number;
  expected_calibration_error: number;
  maximum_calibration_error: number;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
}

export interface BenchmarkResponse {
  evaluation_profile: string;
  overall_metrics: BenchmarkMetrics;
  length_slice_metrics: Record<string, BenchmarkMetrics>;
  adversarial_robustness: {
    average_score_drift: number;
    adversarial_tests: Array<{
      sample_id: string;
      attack_type: string;
      clean_score: number;
      perturbed_score: number;
      score_drift: number;
      retained_detection: boolean;
    }>;
  };
  sample_results: Array<{
    id: string;
    genre: string;
    model_family: string;
    word_count: number;
    ground_truth_is_ai: number;
    calibrated_ai_prob: number;
    verdict: string;
    confidence: number;
  }>;
}

export interface SystemHealth {
  status: string;
  version: string;
  device: string;
  cuda_available: boolean;
  active_detectors: string[];
  supported_file_types: string[];
}

