import type { MarketingPlan } from "../types";
import { client } from "./client";

export async function generateMarketingPlan(payload: {
  goal: string;
  dish: string;
  promotion: string;
  target_customer: string;
  date_range: string;
}): Promise<MarketingPlan> {
  const { data } = await client.post<MarketingPlan>("/api/marketing/generate", payload);
  return data;
}
