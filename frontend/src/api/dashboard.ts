import type { DashboardOverview } from "../types";
import { client } from "./client";

export async function fetchDashboard(): Promise<DashboardOverview> {
  const { data } = await client.get<DashboardOverview>("/api/dashboard/overview");
  return data;
}
