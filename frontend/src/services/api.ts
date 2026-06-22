// src/services/api.ts — All backend API calls

import axios, { AxiosError } from "axios";
import { AnalyzeResponse, AnalyzeError } from "@/types/review";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 90_000,   // scraping can take time
  headers: { "Content-Type": "application/json" },
});

// ── Analyze ──────────────────────────────────────────────────────────────────

export async function analyzeProduct(
  url: string
): Promise<AnalyzeResponse> {
  try {
    const { data } = await client.post<AnalyzeResponse>("/analyze", { url });
    return data;
  } catch (err) {
    const axiosErr = err as AxiosError<AnalyzeError>;
    const respData = axiosErr.response?.data;

    // Backend HTTPException wraps detail as an object: { detail: { success, message, detail } }
    // Handle both direct error responses and nested detail objects
    let serverMsg: string | undefined;
    if (respData?.message) {
      serverMsg = respData.message;
    } else if (respData?.detail) {
      if (typeof respData.detail === "string") {
        serverMsg = respData.detail;
      } else if (typeof respData.detail === "object" && respData.detail !== null) {
        const detailObj = respData.detail as Record<string, unknown>;
        serverMsg = (detailObj.message as string) || (detailObj.detail as string) || JSON.stringify(detailObj);
      }
    }
    serverMsg = serverMsg || axiosErr.message;
    throw new Error(serverMsg || "Unable to analyze product. Please try again.");
  }
}

// ── Cache invalidation ────────────────────────────────────────────────────────

export async function clearCache(url: string): Promise<void> {
  await client.delete(`/analyze/cache?url=${encodeURIComponent(url)}`);
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<boolean> {
  try {
    const { data } = await client.get("/health");
    return data.status === "ok";
  } catch {
    return false;
  }
}
