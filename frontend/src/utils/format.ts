export function formatMoney(value: number | string): string {
  const amount = Number(value || 0);
  return `¥${amount.toLocaleString("zh-CN", { maximumFractionDigits: 0 })}`;
}

export function formatPercent(value: number): string {
  return `${value}%`;
}

export function levelColor(level: string): string {
  if (level.includes("高价值沉睡")) return "red";
  if (level.includes("高价值")) return "gold";
  if (level.includes("沉睡")) return "orange";
  if (level.includes("潜力")) return "blue";
  return "default";
}

export function riskColor(risk: string): string {
  if (risk === "高") return "#b5453a";
  if (risk === "中") return "#c9842a";
  return "#2f6f5e";
}
