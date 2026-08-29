import { Button, Card, Tag } from "antd";
import type { OpportunityItem } from "../../types";
import { formatMoney } from "../../utils/format";

const levelColor: Record<string, string> = {
  high: "red",
  medium: "orange",
  low: "green",
};

const statusColor: Record<string, string> = {
  pending: "gold",
  processing: "blue",
  completed: "default",
  ignored: "default",
};

export default function OpportunityCard({
  item,
  onOpen,
}: {
  item: OpportunityItem;
  onOpen: (item: OpportunityItem) => void;
}) {
  return (
    <Card
      hoverable
      className={item.level === "high" ? "opp-card opp-card-high" : "opp-card"}
      onClick={() => onOpen(item)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <Tag color={levelColor[item.level] || "default"}>
          {item.level_label} · {item.type_label}
        </Tag>
        <Tag color={statusColor[item.status]}>{item.status_label}</Tag>
      </div>
      <h4 style={{ margin: "10px 0 8px" }}>{item.title}</h4>
      <p style={{ minHeight: 48, color: "#4b5563" }}>{item.description}</p>
      <div style={{ color: "#6b7280", fontSize: 13 }}>优先级 {item.priority}</div>
      <div style={{ margin: "6px 0" }}>
        预计影响 {formatMoney(item.estimated_impact)}
        <span className="demo-note"> 模拟估算</span>
      </div>
      <div style={{ marginBottom: 12 }}>{item.suggestion}</div>
      <Button type="link" style={{ padding: 0 }} onClick={() => onOpen(item)}>
        查看详情
      </Button>
    </Card>
  );
}
