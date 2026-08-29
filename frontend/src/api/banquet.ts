import type {
  BanquetAnalyzeResult,
  BanquetLeadItem,
  BanquetLeadListResponse,
} from "../types";
import { client } from "./client";

export async function fetchBanquetLeads(status?: string): Promise<BanquetLeadListResponse> {
  const { data } = await client.get<BanquetLeadListResponse>("/api/banquet-leads", {
    params: status ? { status } : undefined,
  });
  return data;
}

export async function createBanquetLead(payload: {
  customer_name: string;
  phone: string;
  event_type: string;
  people_count: number;
  expected_amount: string;
  event_date?: string | null;
  source: string;
  status?: string;
  notes?: string;
}): Promise<BanquetLeadItem> {
  const { data } = await client.post<BanquetLeadItem>("/api/banquet-leads", payload);
  return data;
}

export async function updateBanquetLead(
  id: number,
  payload: { status?: string; notes?: string },
): Promise<BanquetLeadItem> {
  const { data } = await client.patch<BanquetLeadItem>(`/api/banquet-leads/${id}`, payload);
  return data;
}

export async function analyzeBanquetLead(id: number): Promise<BanquetAnalyzeResult> {
  const { data } = await client.post<BanquetAnalyzeResult>(`/api/banquet-leads/${id}/analyze`);
  return data;
}
