import axios from "axios";
import type {
  ProcessResponse,
  StatusResponse,
  ResultResponse,
} from "../types/invoice";

const api = axios.create({
  baseURL: "/api",
});

export async function processInvoice(file: File): Promise<ProcessResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post<ProcessResponse>("/process", formData);
  return response.data;
}

export async function getStatus(jobId: string): Promise<StatusResponse> {
  const response = await api.get<StatusResponse>(`/status/${jobId}`);
  return response.data;
}

export async function getResult(jobId: string): Promise<ResultResponse> {
  const response = await api.get<ResultResponse>(`/result/${jobId}`);
  return response.data;
}
