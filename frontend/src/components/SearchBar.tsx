"use client";
// src/components/SearchBar.tsx

import { useState, KeyboardEvent } from "react";
import { Search, Link, AlertCircle } from "lucide-react";
import clsx from "clsx";

// ── Supported platforms ──────────────────────────────────────────────────────
const SUPPORTED_PLATFORMS = [
  { name: "Myntra",           domain: "myntra.com",          color: "#FF3F6C" },
  { name: "Ajio",             domain: "ajio.com",            color: "#E94560" },
  { name: "Nykaa Fashion",    domain: "nykaa.com",           color: "#FC2779" },
  { name: "The Souled Store", domain: "thesouledstore.com",  color: "#1A1A2E" },
  { name: "Snitch",           domain: "snitch.co.in",        color: "#000000" },
  { name: "Bewakoof",         domain: "bewakoof.com",        color: "#F7C300" },
  { name: "Bonkers Corner",   domain: "bonkerscorner.com",   color: "#FF6B35" },
  { name: "Tata CLiQ Fashion","domain": "tatacliq.com",      color: "#4B1E7F" },
];

const BLOCKED_DOMAINS = [
  "amazon", "flipkart", "walmart", "meesho", "snapdeal",
  "paytm", "shopclues", "ebay", "alibaba",
];

const EXAMPLE_URLS = [
  {
    label: "Myntra — HRX Shorts",
    url: "https://www.myntra.com/shorts/hrx+by+hrithik+roshan/hrx-by-hrithik-roshan-men-brand-logo-printed-shorts/39954510/buy",
  },
  {
    label: "Myntra — Sangria Dress",
    url: "https://www.myntra.com/ethnic-dresses/sangria/sangria-girls-embroidered-maxi-fit-and-flare-dress-with-dupatta/32650399/buy",
  },
];

// ── Helpers ──────────────────────────────────────────────────────────────────
function isBlockedDomain(url: string): string | null {
  const lower = url.toLowerCase();
  for (const d of BLOCKED_DOMAINS) {
    if (lower.includes(d)) return d;
  }
  return null;
}

function isSupportedDomain(url: string): boolean {
  const lower = url.toLowerCase();
  return SUPPORTED_PLATFORMS.some((p) => lower.includes(p.domain));
}

interface Props {
  onScan: (url: string) => void;
  disabled?: boolean;
}

export default function SearchBar({ onScan, disabled }: Props) {
  const [url, setUrl]         = useState("");
  const [touched, setTouched] = useState(false);

  const trimmed    = url.trim();
  const isHttp     = trimmed.startsWith("http");
  const blocked    = isHttp ? isBlockedDomain(trimmed) : null;
  const isSupported = isHttp && isSupportedDomain(trimmed);

  // Error states
  const notHttpErr  = touched && trimmed !== "" && !isHttp;
  const blockedErr  = touched && isHttp && blocked !== null;
  const notSupportedErr = touched && isHttp && !blocked && !isSupported && trimmed !== "";

  const canScan = isHttp && isSupported && !disabled;

  function handleScan() {
    setTouched(true);
    if (!canScan) return;
    onScan(trimmed);
  }

  function handleKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleScan();
  }

  function handleChange(val: string) {
    setUrl(val);
    setTouched(false);
  }

  return (
    <div className="input-card">
      {/* ── Supported platform chips ────────────────────────────── */}
      <div style={{ marginBottom: 16 }}>
        <p className="input-label" style={{ marginBottom: 10 }}>
          Supported Platforms
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {SUPPORTED_PLATFORMS.map((p) => (
            <span
              key={p.domain}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "4px 12px",
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 600,
                background: "rgba(255,255,255,0.06)",
                border: `1px solid ${p.color}44`,
                color: p.color === "#000000" || p.color === "#1A1A2E" ? "#e0e0e0" : p.color,
                letterSpacing: "0.02em",
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: p.color,
                  flexShrink: 0,
                }}
              />
              {p.name}
            </span>
          ))}
        </div>
      </div>

      {/* ── URL input ───────────────────────────────────────────── */}
      <p className="input-label">Paste Product URL</p>

      <div className="url-row">
        <div className="input-wrap">
          <Link size={16} className="input-icon" />
          <input
            className={clsx(
              "url-input",
              (notHttpErr || blockedErr || notSupportedErr) && "url-input--error"
            )}
            type="url"
            placeholder="https://www.myntra.com/... or https://www.ajio.com/..."
            value={url}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={() => setTouched(true)}
            onKeyDown={handleKey}
            disabled={disabled}
            aria-label="Product URL"
            aria-invalid={notHttpErr || blockedErr || notSupportedErr}
          />
        </div>

        <button
          className="scan-btn"
          onClick={handleScan}
          disabled={!canScan || !trimmed}
          aria-label="Scan product"
        >
          <Search size={16} style={{ display: "inline", marginRight: 8 }} />
          Scan Product
        </button>
      </div>

      {/* ── Error messages ──────────────────────────────────────── */}
      {notHttpErr && (
        <p className="error-msg" role="alert" style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <AlertCircle size={14} />
          Please enter a valid URL starting with https://
        </p>
      )}

      {blockedErr && (
        <p className="error-msg" role="alert" style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <AlertCircle size={14} />
          <span>
            <strong style={{ textTransform: "capitalize" }}>{blocked}</strong> is not supported.
            TruthLens works with Indian fashion platforms like Myntra, Ajio, Nykaa, Snitch, and more.
          </span>
        </p>
      )}

      {notSupportedErr && (
        <p className="error-msg" role="alert" style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <AlertCircle size={14} />
          This platform is not supported. Please paste a link from Myntra, Ajio, Nykaa Fashion,
          The Souled Store, Snitch, Bewakoof, Bonkers Corner, or Tata CLiQ Fashion.
        </p>
      )}

      {/* ── Example links ───────────────────────────────────────── */}
      <div className="examples">
        <span className="input-label" style={{ marginBottom: 0, paddingTop: 2 }}>
          Try:
        </span>
        {EXAMPLE_URLS.map((ex) => (
          <button
            key={ex.url}
            className="example-chip"
            onClick={() => { handleChange(ex.url); }}
            disabled={disabled}
          >
            {ex.label}
          </button>
        ))}
      </div>
    </div>
  );
}
