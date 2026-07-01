"use client";
// src/app/page.tsx

import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import { useScan } from "@/hooks/useScan";
import SearchBar    from "@/components/SearchBar";
import ScanLoader   from "@/components/ScanLoader";
import TrustScore   from "@/components/TrustScore";
import VerdictCard  from "@/components/VerdictCard";
import RedFlags     from "@/components/RedFlags";
import ReviewDNA    from "@/components/ReviewDNA";
import Charts       from "@/components/Charts";
import AIExplanation from "@/components/AIExplanation";
import styles       from "./page.module.css";

export default function Home() {
  const { state, result, error, activeStep, progress, scan, reset } = useScan();

  const isScanning = state === "scanning";
  const isDone     = state === "done";
  const isError    = state === "error";

  return (
    <main className={styles.app}>
      <div className={styles.gridBg} aria-hidden />

      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          AI-Powered · Fraud Detection
        </div>
        <h1>
          Truth<span className={styles.accent}>Lens</span>
        </h1>
        <p className={styles.subtitle}>
          We don't just detect fake reviews — we explain them.
        </p>
      </header>

      {/* ── Search ─────────────────────────────────────────────────── */}
      <SearchBar onScan={scan} disabled={isScanning} />

      {/* ── Loader ─────────────────────────────────────────────────── */}
      <AnimatePresence>
        {(isScanning || isError) && (
          <ScanLoader
            activeStep={activeStep}
            progress={progress}
            error={isError ? error : null}
            onRetry={reset}
          />
        )}
      </AnimatePresence>

      {/* ── Results ────────────────────────────────────────────────── */}
      <AnimatePresence>
        {isDone && result && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            aria-label="Analysis results"
          >

            <TrustScore
              score={result.trust_score}
              riskLevel={result.risk_level}
              verdict={result.verdict}
              productTitle={result.product_title}
              totalReviews={result.total_reviews_analyzed}
              cached={result.cached}
              demoMode={result.demo_mode}
            />

            <VerdictCard verdict={result.verdict} riskLevel={result.risk_level} />

            <div className={styles.grid2col}>
              <RedFlags flags={result.flags} />
              <ReviewDNA dna={result.dna} />
            </div>

            <Charts charts={result.charts} />

            <AIExplanation
              explanation={result.explanation}
              sentimentSummary={result.sentiment_summary}
            />

            <div style={{ textAlign: "center", marginTop: 24 }}>
              <button className={styles.resetBtn} onClick={reset}>
                ← Scan another product
              </button>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </main>
  );
}
