import { Alert, Button, Card, Col, Row, Spin } from "antd";
import { useState } from "react";
import { diagnoseMenu } from "../../api/ops";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader from "../../components/PageHeader";

export default function MenuDiagnosis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  const run = async () => {
    setLoading(true);
    try {
      setData(await diagnoseMenu());
      setError("");
    } catch (err) {
      setError(getErrorMessage(err, AI_UNAVAILABLE));
    } finally {
      setLoading(false);
    }
  };

  const list = (key: string) => (Array.isArray(data?.[key]) ? (data?.[key] as string[]) : []);

  return (
    <div>
      <PageHeader
        title="AI菜单诊断"
        extra={
          <Button type="primary" loading={loading} onClick={() => void run()}>
            AI诊断菜单
          </Button>
        }
      >
        告诉老板哪些菜该推、哪些菜该关注。菜品成本为模拟数据。
      </PageHeader>
      {error ? <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} /> : null}
      {loading && !data ? <Spin /> : null}
      {data ? (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card>
                <div style={{ color: "#6b7280" }}>菜单健康度</div>
                <div style={{ fontSize: 36, fontWeight: 600 }}>{String(data.health_score || 78)}分</div>
              </Card>
            </Col>
            <Col span={16}>
              <Card title="AI判断">{String(data.judgment || "")}</Card>
            </Col>
          </Row>
          <AiResultCard title="AI菜单诊断报告" demoFallback={Boolean(data.demo_fallback)}>
            <Section title="应重点推广" items={list("stars")} />
            <Section title="值得重点推荐" items={list("potentials")} />
            <Section title="引流菜，控制成本" items={list("traffic")} />
            <Section title="需要关注" items={list("eliminate")} />
            <h4>菜单整体建议</h4>
            <p>{String(data.structure_issue || "")}</p>
            <ol>
              {list("suggestions").map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
          </AiResultCard>
        </>
      ) : (
        <Card>点击「AI诊断菜单」，系统会按销量和毛利率给出明星菜、潜力菜、引流菜和淘汰候选。</Card>
      )}
    </div>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="diag-item">
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
