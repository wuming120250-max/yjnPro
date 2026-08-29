import type { ReviewAnalyzeResult, ReviewListResponse } from "../types";
import { client } from "./client";

export async function fetchReviews(params?: {
  sentiment?: string;
  source?: string;
}): Promise<ReviewListResponse> {
  const { data } = await client.get<ReviewListResponse>("/api/reviews", { params });
  return data;
}

export async function analyzeReviews(): Promise<ReviewAnalyzeResult> {
  const { data } = await client.post<ReviewAnalyzeResult>("/api/reviews/analyze");
  return data;
}
