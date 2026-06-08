import { useState, useRef, useCallback } from "react";
import type { StatusResponse, InvoiceJSON } from "../types/invoice";
import { processInvoice, getStatus, getResult } from "../services/api";

interface UseProcessInvoiceReturn {
  upload: (file: File) => void;
  status: StatusResponse | null;
  result: InvoiceJSON | null;
  error: string | null;
  isProcessing: boolean;
}

function useProcessInvoice(): UseProcessInvoiceReturn {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [result, setResult] = useState<InvoiceJSON | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const upload = useCallback(
    async (file: File) => {
      setIsProcessing(true);
      setError(null);
      setResult(null);
      setStatus(null);
      stopPolling();

      try {
        const response = await processInvoice(file);
        const jobId = response.job_id;

        intervalRef.current = setInterval(async () => {
          try {
            const statusRes = await getStatus(jobId);
            setStatus(statusRes);

            if (statusRes.status === "completed") {
              stopPolling();
              const resultRes = await getResult(jobId);
              setResult(resultRes.result);
              setIsProcessing(false);
            } else if (statusRes.status === "failed") {
              stopPolling();
              const resultRes = await getResult(jobId);
              setError(resultRes.error || "Processing failed");
              setIsProcessing(false);
            }
          } catch (e) {
            stopPolling();
            setError("Failed to check status");
            setIsProcessing(false);
          }
        }, 2000);
      } catch (e) {
        setError("Failed to upload file");
        setIsProcessing(false);
      }
    },
    [stopPolling]
  );

  return { upload, status, result, error, isProcessing };
}

export default useProcessInvoice;
