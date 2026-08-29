import { Button, Space, Tag } from "antd";
import type { OpportunityItem } from "../../types";
import { formatMoney } from "../../utils/format";

export default function TodayPriority({
  item,
  onOpen,
  onCreate,
}: {
  item: OpportunityItem | null;
  onOpen: (item: OpportunityItem) => void;
  onCreate: (item: OpportunityItem) => void;
}) {
  if (!item) return null;
  return (
    <div className="today-priority">
      <Tag color="red">今日最值得做</Tag>
      <h3>{item.title}</h3>
      <p>{item.summary || item.description}</p>
      <div style={{ color: "#6b7280", marginBottom: 6 }}>原因：{item.reason}</div>
      <div>
        预计影响：每周约 {formatMoney(item.estimated_impact)} {item.impact_type_label}机会
        <span className="demo-note">（模拟估算）</span>
      </div>
      <div style={{ margin: "8px 0 16px" }}>AI建议：{item.suggestion}</div>
      <Space>
        <Button type="primary" onClick={() => onOpen(item)}>
          查看分析
        </Button>
        <Button onClick={() => onCreate(item)}>创建任务</Button>
      </Space>
    </div>
  );
}
