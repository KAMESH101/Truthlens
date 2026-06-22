"use client";
// src/components/ScanLoader.tsx

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, Circle, Loader2 } from "lucide-react";
import { SCAN_STEPS } from "@/types/review";

interface Props {
  activeStep: number;
  progress: number;
  error: string | null;
  onRetry: () => void;
}

export default function ScanLoader({ activeStep, progress, error, onRetry }: Props) {
  if (error) {
    return (
      <motion.div
        className="loader"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ display: "block" }}
      >
        <div style={{ textAlign: "center", padding: "1rem 0" }}>
          <p style={{ color: "var(--red)", fontSize: 14, marginBottom: 16 }}>⚠️ {error}</p>
          <button className="scan-btn" onClick={onRetry}>Retry</button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="loader"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ display: "block" }}
    >
      <div className="loader-steps">
        {SCAN_STEPS.map((step, i) => {
          const isDone   = i < activeStep;
          const isActive = i === activeStep;

          return (
            <motion.div
              key={step.id}
              className={`loader-step ${isDone ? "done" : ""} ${isActive ? "active" : ""}`}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <div className="step-icon">
                {isDone ? (
                  <CheckCircle size={14} color="var(--green)" />
                ) : isActive ? (
                  <Loader2 size={14} color="var(--purple)" className="spin" />
                ) : (
                  <span style={{ fontSize: 13 }}>{step.icon}</span>
                )}
              </div>
              <span>{step.label}</span>
            </motion.div>
          );
        })}
      </div>

      <div className="progress-bar-wrap">
        <motion.div
          className="progress-bar"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
      <p style={{ textAlign: "right", fontSize: 12, color: "var(--text-dimmer)", marginTop: 8, fontFamily: "var(--mono)" }}>
        {progress}%
      </p>
    </motion.div>
  );
}
