import { StarOutlined } from "@ant-design/icons";
import { Alert, Card } from "antd";
import type { ReactNode } from "react";

interface Props {
  title?: string;
  demoFallback?: boolean;
  children: ReactNode;
}

export default function AiResultCard({ title = "AI分析结果", demoFallback, children }: Props) {
  return (
    <Card
      title={
        <span>
          <StarOutlined style={{ color: "#c9a227", marginRight: 8 }} />
          {title}
        </span>
      }
      style={{ borderColor: "#eadfce" }}
    >
      {demoFallback ? (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message="当前为演示模式，展示的是预设 AI 分析结果。"
        />
      ) : null}
      {children}
    </Card>
  );
}
