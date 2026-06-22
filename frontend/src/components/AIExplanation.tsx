"use client";
// src/components/AIExplanation.tsx

import { motion } from "framer-motion";

interface Props {
  explanation: string;
  sentimentSummary: string;
}

export default function AIExplanation({ explanation, sentimentSummary }: Props) {
  return (
    <motion.div
      className="section-card ai-explanation"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>🧠</span>
        <h3 className="section-title" style={{ margin: 0 }}>AI Explanation</h3>
        <span style={{
          marginLeft: "auto", fontFamily: "var(--mono)", fontSize: 10,
          color: "var(--purple)", background: "var(--purple-dim)",
          border: "1px solid rgba(139,92,246,0.3)", borderRadius: 4,
          padding: "2px 8px",
        }}>
          OpenRouter · Mixtral 8x7B
        </span>
      </div>

      <p style={{ fontSize: 14, color: "var(--text-dim)", lineHeight: 1.7, marginBottom: 14 }}>
        {explanation}
      </p>

      {sentimentSummary && (
        <div style={{
          borderTop: "1px solid var(--border)",
          paddingTop: 12,
          fontSize: 13,
          color: "var(--text-dimmer)",
          fontStyle: "italic",
        }}>
          {sentimentSummary}
        </div>
      )}
    </motion.div>
  );
}
