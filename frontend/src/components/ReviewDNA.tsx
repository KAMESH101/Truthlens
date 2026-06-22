"use client";
// src/components/ReviewDNA.tsx

import { motion } from "framer-motion";
import { ReviewDNA as ReviewDNAType } from "@/types/review";

interface Props {
  dna: ReviewDNAType;
}

export default function ReviewDNA({ dna }: Props) {
  const sim = Math.round(dna.similarity_percent);

  const color =
    sim >= 60 ? "var(--red)" :
    sim >= 30 ? "var(--yellow)" :
                "var(--green)";

  return (
    <div className="section-card">
      <h3 className="section-title">🧬 Review DNA Analysis</h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 16 }}>
        {[
          { label: "Similarity", value: `${sim}%` },
          { label: "Duplicates",  value: dna.duplicate_count },
          { label: "Clusters",    value: dna.cluster_count },
        ].map((stat) => (
          <div key={stat.label} className="stat-card">
            <p className="stat-label">{stat.label}</p>
            <p className="stat-value" style={{ color: stat.label === "Similarity" ? color : "var(--text)" }}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Similarity bar */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
          <span style={{ fontSize: 12, color: "var(--text-dimmer)", fontFamily: "var(--mono)" }}>
            Review DNA Similarity
          </span>
          <span style={{ fontSize: 12, color, fontFamily: "var(--mono)", fontWeight: 600 }}>
            {sim}%
          </span>
        </div>
        <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 100, overflow: "hidden" }}>
          <motion.div
            style={{ height: "100%", borderRadius: 100, background: color }}
            initial={{ width: "0%" }}
            animate={{ width: `${sim}%` }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Pattern notes from AI */}
      {dna.pattern_notes.length > 0 && (
        <div>
          <p style={{ fontSize: 12, color: "var(--text-dimmer)", fontFamily: "var(--mono)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.1em" }}>
            Pattern Observations
          </p>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6 }}>
            {dna.pattern_notes.map((note, i) => (
              <li key={i} style={{ fontSize: 13, color: "var(--text-dim)", display: "flex", gap: 8 }}>
                <span style={{ color: "var(--purple)", flexShrink: 0 }}>›</span>
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
