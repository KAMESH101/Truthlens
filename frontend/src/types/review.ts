// src/types/review.ts — All shared TypeScript types

export type RiskLevel = "safe" | "caution" | "risky";

export interface RedFlag {
  title: string;
  detail: string;
  severity: "high" | "medium" | "low";
}

export interface ReviewDNA {
  similarity_percent: number;
  duplicate_count: number;
  cluster_count: number;
  pattern_notes: string[];
}

export interface ChartDataPoint {
  label: string;
  value: number;
}

export interface ChartsData {
  review_timeline: ChartDataPoint[];
  rating_distribution: ChartDataPoint[];
  sentiment_breakdown: ChartDataPoint[];
}

export interface AnalyzeResponse {
  success: boolean;
  product_title: string | null;
  total_reviews_analyzed: number;
  trust_score: number;
  risk_level: RiskLevel;
  verdict: string;
  flags: RedFlag[];
  dna: ReviewDNA;
  charts: ChartsData;
  sentiment_summary: string;
  explanation: string;
  cached: boolean;
  demo_mode: boolean;
}

export interface AnalyzeError {
  success: false;
  message: string;
  detail?: string | Record<string, unknown>;
}

export type ScanStep = {
  id: string;
  label: string;
  icon: string;
};

export const SCAN_STEPS: ScanStep[] = [
  { id: "scraping",  label: "Scanning product page...",    icon: "🔍" },
  { id: "parsing",   label: "Extracting reviews...",        icon: "📄" },
  { id: "detecting", label: "Detecting patterns...",        icon: "🧬" },
  { id: "ai",        label: "Running AI analysis...",       icon: "🤖" },
  { id: "done",      label: "Generating report...",         icon: "⚠️" },
];
