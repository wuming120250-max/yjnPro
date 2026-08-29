import axios, { AxiosError } from "axios";

const TOKEN_KEY = "yjn_token";

export const client = axios.create({
  baseURL: "",
  timeout: 90000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getErrorMessage(error: unknown, fallback = "请求失败，请稍后重试"): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.message === "Network Error") {
      return "网络异常，请检查后端服务是否已启动";
    }
  }
  return fallback;
}

export const AI_UNAVAILABLE = "AI服务暂时不可用，请稍后重试。";

export { TOKEN_KEY };
