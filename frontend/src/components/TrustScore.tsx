"use client";
// src/components/TrustScore.tsx

import { useEffect, useState } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { motion } from "framer-motion";
import { RiskLevel } from "@/types/review";

const COLORS: Record<RiskLevel, { stroke: string; text: string; badge: string; label: string }> = {
  safe:    { stroke: "#22d3a0", text: "#22d3a0", badge: "badge--green", label: "Safe" },
  caution: { stroke: "#f59e0b", text: "#f59e0b", badge: "badge--yellow", label: "Caution" },
  risky:   { stroke: "#f43f5e", text: "#f43f5e", badge: "badge--red",  label: "Risky" },
};

interface Props {
  score: number;
  riskLevel: RiskLevel;
  verdict: string;
  productTitle: string | null;
  totalReviews: number;
  cached: boolean;
  demoMode: boolean;
}

export default function TrustScore({ score, riskLevel, verdict, productTitle, totalReviews, cached, demoMode }: Props) {
  const [displayed, setDisplayed] = useState(0);
  const colors = COLORS[riskLevel];

  useEffect(() => {
    const timeout = setTimeout(() => setDisplayed(score), 200);
    return () => clearTimeout(timeout);
  }, [score]);

  return (
    <motion.div
      className="trust-hero"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div style={{ width: 130, flexShrink: 0 }}>
        <CircularProgressbar
          value={displayed}
          text={`${displayed}`}
          strokeWidth={10}
          styles={buildStyles({
            pathColor:        colors.stroke,
            textColor:        colors.text,
            trailColor:       "rgba(255,255,255,0.06)",
            textSize:         "26px",
            pathTransitionDuration: 1.4,
          })}
        />
        <p style={{ textAlign: "center", fontSize: 11, color: "var(--text-dimmer)", marginTop: 6, fontFamily: "var(--mono)" }}>
          / 100
        </p>
      </div>

      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <span className={`risk-badge ${colors.badge}`}>{colors.label}</span>
          {cached && (
            <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--text-dimmer)", background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)", borderRadius: 4, padding: "2px 8px" }}>
              cached
            </span>
          )}
        </div>
        <h2 style={{ fontSize: "clamp(1.1rem,2.5vw,1.5rem)", fontWeight: 700, color: "#fff", marginBottom: 8, lineHeight: 1.2 }}>
          {verdict}
        </h2>
        {productTitle && (
          <p style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 4 }}>
            {productTitle}
          </p>
        )}
        <p style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--text-dimmer)" }}>
          {totalReviews} reviews analyzed
        </p>
      </div>
    </motion.div>
  );
}
