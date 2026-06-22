"use client";
// src/components/VerdictCard.tsx

import { motion } from "framer-motion";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";
import { RiskLevel } from "@/types/review";

const CONFIG: Record<RiskLevel, { icon: typeof ShieldCheck; color: string; bg: string }> = {
  safe:    { icon: ShieldCheck, color: "var(--green)",  bg: "var(--green-dim)" },
  caution: { icon: Shield,      color: "var(--yellow)", bg: "var(--yellow-dim)" },
  risky:   { icon: ShieldAlert, color: "var(--red)",    bg: "var(--red-dim)" },
};

interface Props {
  verdict: string;
  riskLevel: RiskLevel;
}

export default function VerdictCard({ verdict, riskLevel }: Props) {
  const { icon: Icon, color, bg } = CONFIG[riskLevel];

  return (
    <motion.div
      style={{
        background: bg,
        border: `1px solid ${color}33`,
        borderRadius: 12,
        padding: "1rem 1.25rem",
        display: "flex",
        alignItems: "center",
        gap: 14,
        marginBottom: "1rem",
      }}
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.15 }}
    >
      <Icon size={28} color={color} />
      <div>
        <p style={{ fontSize: 11, color, fontFamily: "var(--mono)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>
          AI Verdict
        </p>
        <p style={{ fontSize: 16, fontWeight: 700, color: "#fff" }}>{verdict}</p>
      </div>
    </motion.div>
  );
}
