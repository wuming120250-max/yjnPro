import { client } from "./client";
import type { OpportunityItem, OpportunityListResponse } from "../types";

export async function fetchOpportunities(params?: {
  type?: string;
  level?: string;
  status?: string;
}): Promise<OpportunityListResponse> {
  const { data } = await client.get<OpportunityListResponse>("/api/opportunities", { params });
  return data;
}

export async function generateOpportunities(force = false): Promise<OpportunityListResponse> {
  const { data } = await client.post<OpportunityListResponse>("/api/opportunities/generate", null, {
    params: { force },
  });
  return data;
}

export async function fetchOpportunity(id: number): Promise<OpportunityItem> {
  const { data } = await client.get<OpportunityItem>(`/api/opportunities/${id}`);
  return data;
}

export async function analyzeOpportunity(id: number): Promise<OpportunityItem> {
  const { data } = await client.post<OpportunityItem>(`/api/opportunities/${id}/analyze`);
  return data;
}

export async function processOpportunity(id: number): Promise<OpportunityItem> {
  const { data } = await client.post<OpportunityItem>(`/api/opportunities/${id}/processing`);
  return data;
}

export async function completeOpportunity(id: number): Promise<OpportunityItem> {
  const { data } = await client.post<OpportunityItem>(`/api/opportunities/${id}/complete`);
  return data;
}

export async function ignoreOpportunity(id: number): Promise<OpportunityItem> {
  const { data } = await client.post<OpportunityItem>(`/api/opportunities/${id}/ignore`);
  return data;
}
