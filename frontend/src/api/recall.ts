import type { RecallAnalyzeResult, RecallListResponse, RecallMessageResult } from "../types";
import { client } from "./client";

export async function fetchRecallCustomers(): Promise<RecallListResponse> {
  const { data } = await client.get<RecallListResponse>("/api/recall/customers");
  return data;
}

export async function analyzeRecallCustomer(id: number): Promise<RecallAnalyzeResult> {
  const { data } = await client.post<RecallAnalyzeResult>(`/api/recall/${id}/analyze`);
  return data;
}

export async function generateRecallMessage(id: number): Promise<RecallMessageResult> {
  const { data } = await client.post<RecallMessageResult>(`/api/recall/${id}/generate-message`);
  return data;
}
