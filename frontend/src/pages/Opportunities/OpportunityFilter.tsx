import { Radio, Space } from "antd";

const TYPES = [
  { value: "", label: "全部" },
  { value: "revenue", label: "营业" },
  { value: "menu", label: "菜品" },
  { value: "customer", label: "客户" },
  { value: "service", label: "服务" },
  { value: "banquet", label: "宴请" },
];

const LEVELS = [
  { value: "", label: "全部优先级" },
  { value: "high", label: "高优先级" },
  { value: "medium", label: "中优先级" },
  { value: "low", label: "普通" },
];

export default function OpportunityFilter({
  type,
  level,
  onChange,
}: {
  type: string;
  level: string;
  onChange: (next: { type: string; level: string }) => void;
}) {
  return (
    <Space wrap size={16} style={{ margin: "16px 0" }}>
      <Radio.Group
        value={type}
        onChange={(event) => onChange({ type: event.target.value, level })}
        optionType="button"
        options={TYPES}
      />
      <Radio.Group
        value={level}
        onChange={(event) => onChange({ type, level: event.target.value })}
        optionType="button"
        options={LEVELS}
      />
    </Space>
  );
}
