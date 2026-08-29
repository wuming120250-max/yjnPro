import type { AppSettings, LoginResponse } from "../types";
import { client, TOKEN_KEY } from "./client";

export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await client.post<LoginResponse>("/api/auth/login", { username, password });
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem("yjn_username", data.username);
  localStorage.setItem("yjn_store", data.store_name);
  return data;
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("yjn_username");
  localStorage.removeItem("yjn_store");
}

export async function fetchSettings(): Promise<AppSettings> {
  const { data } = await client.get<AppSettings>("/api/auth/settings");
  return data;
}

export function isLoggedIn(): boolean {
  return Boolean(localStorage.getItem(TOKEN_KEY));
}
