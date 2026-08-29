import { Button, Descriptions, Drawer, Space, Tag } from "antd";
import type { OpportunityItem } from "../../types";
import { formatMoney } from "../../utils/format";

const levelColor: Record<string, string> = {
  high: "red",
  medium: "orange",
  low: "green",
};

export default function OpportunityDetail({
  item,
  open,
  analyzing,
  onClose,
  onAnalyze,
  onProcess,
  onComplete,
  onIgnore,
  onJump,
}: {
  item: OpportunityItem | null;
  open: boolean;
  analyzing: boolean;
  onClose: () => void;
  onAnalyze: () => void;
  onProcess: () => void;
  onComplete: () => void;
  onIgnore: () => void;
  onJump: (path: string) => void;
}) {
  const snapshot = item?.data_snapshot || {};
  const evidence = Object.entries(snapshot).filter(([key]) => key !== "action_items" && key !== "samples" && key !== "examples" && key !== "note");

  return (
    <Drawer
      width={480}
      open={open}
      onClose={onClose}
      title={item?.title || "机会详情"}
      extra={item ? <Tag color={levelColor[item.level]}>{item.level_label}</Tag> : null}
    >
      {item ? (
        <div>
          <h4>问题</h4>
          <p>{item.description}</p>
          <h4>数据证据</h4>
          <Descriptions size="small" column={1} bordered>
            {evidence.map(([key, value]) => (
              <Descriptions.Item key={key} label={key}>
                {String(value)}
              </Descriptions.Item>
            ))}
          </Descriptions>
          {item.demo_note ? <p className="demo-note">{item.demo_note}</p> : <p className="demo-note">影响金额为模拟估算</p>}
          <h4>AI判断</h4>
          <p>{item.reason}</p>
          <p>{item.summary}</p>
          <h4>影响</h4>
          <p>
            预计影响：{item.impact_type_label} · {formatMoney(item.estimated_impact)}
            <span className="demo-note">（模拟估算）</span>
          </p>
          <h4>建议</h4>
          <p>{item.suggestion}</p>
          <h4>行动</h4>
          <p>建议今天执行：{item.action}</p>
          <ul>
            {(item.action_items || []).map((line) => (
              <li key={line}>□ {line}</li>
            ))}
          </ul>
          {item.status === "completed" ? <Tag color="green">✓ 已完成</Tag> : null}
          {item.demo_fallback ? <p className="demo-note">AI分析暂时不可用，以上为规则分析结果。</p> : null}
          <Space wrap style={{ marginTop: 16 }}>
            <Button type="primary" loading={analyzing} onClick={onAnalyze}>
              AI分析
            </Button>
            <Button onClick={onProcess}>处理中</Button>
            <Button onClick={onComplete}>完成</Button>
            <Button onClick={onIgnore}>忽略</Button>
            {item.link ? (
              <Button type="link" onClick={() => onJump(item.link)}>
                {jumpLabel(item)}
              </Button>
            ) : null}
          </Space>
        </div>
      ) : null}
    </Drawer>
  );
}

function jumpLabel(item: OpportunityItem) {
  if (item.type === "customer") return "处理（去召回）";
  if (item.type === "menu") return "查看菜品";
  if (item.type === "banquet") return "查看客户";
  if (item.link === "/reviews") return "查看评价";
  if (item.link === "/table-efficiency") return "查看翻台";
  return "查看详情";
}
