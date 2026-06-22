// src/hooks/useScan.ts

import { useState, useCallback, useRef } from "react";
import { analyzeProduct } from "@/services/api";
import { AnalyzeResponse, SCAN_STEPS } from "@/types/review";

export type ScanState = "idle" | "scanning" | "done" | "error";

export function useScan() {
  const [state, setState]           = useState<ScanState>("idle");
  const [result, setResult]         = useState<AnalyzeResponse | null>(null);
  const [error, setError]           = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<number>(-1);
  const [progress, setProgress]     = useState<number>(0);
  const abortRef                    = useRef<AbortController | null>(null);

  const scan = useCallback(async (url: string) => {
    // Reset
    setResult(null);
    setError(null);
    setActiveStep(0);
    setProgress(0);
    setState("scanning");

    // Animate steps while waiting for API
    const stepDuration = 2800;   // ms per step (last step waits for API)
    const stepTimers: ReturnType<typeof setTimeout>[] = [];

    SCAN_STEPS.forEach((_, i) => {
      if (i === 0) return;   // step 0 is already active
      const t = setTimeout(() => {
        setActiveStep(i);
        setProgress(Math.round((i / (SCAN_STEPS.length - 1)) * 85));
      }, stepDuration * i);
      stepTimers.push(t);
    });

    try {
      const data = await analyzeProduct(url);
      stepTimers.forEach(clearTimeout);
      setActiveStep(SCAN_STEPS.length - 1);
      setProgress(100);
      await new Promise((r) => setTimeout(r, 500));   // brief pause before showing results
      setResult(data);
      setState("done");
    } catch (err: unknown) {
      stepTimers.forEach(clearTimeout);
      const msg = err instanceof Error ? err.message : "Scan failed. Please try again.";
      setError(msg);
      setState("error");
      setActiveStep(-1);
    }
  }, []);

  const reset = useCallback(() => {
    setState("idle");
    setResult(null);
    setError(null);
    setActiveStep(-1);
    setProgress(0);
  }, []);

  return { state, result, error, activeStep, progress, scan, reset };
}
