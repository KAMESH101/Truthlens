"use client";
// src/components/Charts.tsx

import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { ChartsData } from "@/types/review";

const PIE_COLORS = ["#22d3a0", "#8b5cf6", "#f43f5e"];

const TOOLTIP_STYLE = {
  background: "#0f0f1a",
  border: "1px solid rgba(139,92,246,0.3)",
  borderRadius: 8,
  fontFamily: "'JetBrains Mono', monospace",
  fontSize: 12,
  color: "#e8e4ff",
};

interface Props {
  charts: ChartsData;
}

const BAR_COLORS = ["#f43f5e", "#f59e0b", "#8b5cf6", "#22d3a0", "#22d3a0"];

export default function Charts({ charts }: Props) {
  return (
    <div className="section-card">
      <h3 className="section-title">📊 Analytics</h3>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Timeline */}
        <div>
          <p className="chart-label">Review Timeline</p>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={charts.review_timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: "rgba(232,228,255,0.4)" }} />
              <YAxis tick={{ fontSize: 10, fill: "rgba(232,228,255,0.4)" }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Line
                type="monotone" dataKey="value" name="Reviews"
                stroke="#8b5cf6" strokeWidth={2} dot={{ fill: "#8b5cf6", r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Rating distribution */}
        <div>
          <p className="chart-label">Rating Distribution</p>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={charts.rating_distribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: "rgba(232,228,255,0.4)" }} />
              <YAxis tick={{ fontSize: 10, fill: "rgba(232,228,255,0.4)" }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="value" name="Reviews" radius={[4, 4, 0, 0]}>
                {charts.rating_distribution.map((_, i) => (
                  <Cell
                    key={i}
                    fill={BAR_COLORS[i] ?? "#8b5cf6"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sentiment */}
      <div style={{ marginTop: 24 }}>
        <p className="chart-label">Sentiment Breakdown</p>
        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={charts.sentiment_breakdown}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="50%"
              outerRadius={70}
              innerRadius={40}
            >
              {charts.sentiment_breakdown.map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => `${v}%`} />
            <Legend
              formatter={(v) => <span style={{ fontSize: 12, color: "rgba(232,228,255,0.6)" }}>{v}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
