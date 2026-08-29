import type { CustomerDetail, CustomerListResponse } from "../types";
import { client } from "./client";

export async function fetchCustomers(params: {
  keyword?: string;
  level?: string;
  tag?: string;
  page?: number;
  page_size?: number;
}): Promise<CustomerListResponse> {
  const { data } = await client.get<CustomerListResponse>("/api/customers", { params });
  return data;
}

export async function fetchCustomer(id: number): Promise<CustomerDetail> {
  const { data } = await client.get<CustomerDetail>(`/api/customers/${id}`);
  return data;
}
