import { client } from "./client";
import type { DailyReport, DashboardOverview, MenuAnalysis } from "../types";

export async function fetchDailyReport(): Promise<DailyReport> {
  const { data } = await client.get<DailyReport>("/api/daily-report");
  return data;
}

export async function generateDailyReport(): Promise<DailyReport> {
  const { data } = await client.post<DailyReport>("/api/daily-report/generate");
  return data;
}

export async function fetchMenuAnalysis(): Promise<MenuAnalysis> {
  const { data } = await client.get<MenuAnalysis>("/api/menu-analysis");
  return data;
}

export async function diagnoseMenu() {
  const { data } = await client.post("/api/menu-analysis/diagnose");
  return data;
}

export async function fetchRevenueAnalysis() {
  const { data } = await client.get("/api/revenue-analysis");
  return data;
}

export async function analyzeRevenue() {
  const { data } = await client.post("/api/revenue-analysis/analyze");
  return data;
}

export async function fetchTableEfficiency() {
  const { data } = await client.get("/api/table-efficiency");
  return data;
}

export async function analyzeTableEfficiency() {
  const { data } = await client.post("/api/table-efficiency/analyze");
  return data;
}

export async function recommendDishes(payload: {
  people: number;
  budget: number;
  scene: string;
  taste: string;
  first_visit: boolean;
  mode: string;
}) {
  const { data } = await client.post("/api/staff-assistant/recommend", payload);
  return data;
}

export async function fetchDashboardV2(): Promise<DashboardOverview> {
  const { data } = await client.get<DashboardOverview>("/api/dashboard/overview");
  return data;
}
