"use client";
// src/components/RedFlags.tsx

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, AlertCircle, Info, ChevronDown } from "lucide-react";
import { RedFlag } from "@/types/review";

const SEVERITY_MAP = {
  high:   { icon: AlertTriangle, color: "var(--red)",    bg: "var(--red-dim)",    label: "High" },
  medium: { icon: AlertCircle,   color: "var(--yellow)", bg: "var(--yellow-dim)", label: "Medium" },
  low:    { icon: Info,          color: "var(--purple)", bg: "var(--purple-dim)", label: "Low" },
};

interface Props {
  flags: RedFlag[];
}

function FlagItem({ flag, index }: { flag: RedFlag; index: number }) {
  const [open, setOpen] = useState(false);
  const sev = flag.severity in SEVERITY_MAP ? flag.severity : "medium";
  const { icon: Icon, color, bg, label } = SEVERITY_MAP[sev as keyof typeof SEVERITY_MAP];

  return (
    <motion.div
      className="flag-card"
      style={{ borderLeftColor: color, background: bg }}
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
    >
      <div
        style={{ display: "flex", alignItems: "flex-start", gap: 10, cursor: "pointer" }}
        onClick={() => setOpen((v) => !v)}
        role="button"
        aria-expanded={open}
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setOpen((v) => !v); }}
      >
        <Icon size={16} color={color} style={{ flexShrink: 0, marginTop: 2 }} />
        <div style={{ flex: 1 }}>
          <p style={{ fontWeight: 600, fontSize: 14, color: "#fff", marginBottom: 0 }}>
            {flag.title}
            <span style={{
              marginLeft: 8, fontFamily: "var(--mono)", fontSize: 10,
              color, border: `1px solid ${color}`, borderRadius: 4, padding: "1px 6px",
            }}>
              {label}
            </span>
          </p>
        </div>
        <ChevronDown
          size={14}
          color={color}
          style={{
            flexShrink: 0, marginTop: 2,
            transition: "transform 0.2s",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
          }}
        />
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{ overflow: "hidden" }}
          >
            <p style={{
              fontSize: 13, color: "var(--text-dim)",
              lineHeight: 1.6, marginTop: 10, paddingLeft: 26,
            }}>
              {flag.detail}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function RedFlags({ flags }: Props) {
  if (!flags.length) {
    return (
      <div className="section-card">
        <h3 className="section-title">🚨 Red Flags</h3>
        <p style={{ color: "var(--green)", fontSize: 14 }}>✓ No significant red flags detected.</p>
      </div>
    );
  }

  return (
    <div className="section-card">
      <h3 className="section-title">🚨 Red Flags <span className="count-badge">{flags.length}</span><span style={{
        marginLeft: "auto", fontFamily: "var(--mono)",
        fontSize: 10, color: "var(--text-dimmer)",
      }}>
        tap to expand
      </span></h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {flags.map((flag, i) => (
          <FlagItem key={i} flag={flag} index={i} />
        ))}
      </div>
    </div>
  );
}
