import { Alert, Button, Card, Col, Row, Spin, Statistic } from "antd";
import { useEffect, useState } from "react";
import { fetchDailyReport, generateDailyReport } from "../../api/ops";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader from "../../components/PageHeader";
import type { DailyReport } from "../../types";
import { formatMoney } from "../../utils/format";

export default function AIDailyReport() {
  const [data, setData] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const load = async (regenerate = false) => {
    if (regenerate) setGenerating(true);
    try {
      setData(regenerate ? await generateDailyReport() : await fetchDailyReport());
      setError("");
    } catch (err) {
      setError(getErrorMessage(err, AI_UNAVAILABLE));
    } finally {
      setGenerating(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(false);
  }, []);

  if (loading) return <Spin />;
  if (error && !data) return <Alert type="error" showIcon message={error} />;
  if (!data) return null;

  return (
    <div>
      <PageHeader
        title="AI老板日报"
        extra={
          <Button type="primary" loading={generating} onClick={() => void load(true)}>
            重新生成日报
          </Button>
        }
      >
        {data.report_date} · 每天告诉老板：今天最该关注什么、最该做什么。
      </PageHeader>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="今日经营评分" value={data.score} suffix={`/ 100  ${data.stars_label}`} />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic title="营业额" value={formatMoney(data.today_revenue)} />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic title="订单" value={data.today_orders} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="客单价" value={formatMoney(data.average_order_amount)} />
          </Card>
        </Col>
      </Row>
      <div style={{ marginTop: 16 }}>
        <AiResultCard title="今日经营总结" demoFallback={data.demo_fallback}>
          <p>{data.summary}</p>
          <h4>AI发现</h4>
          <ol>
            {(data.warnings || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
            {(data.positives || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
            {(data.opportunities || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <div className="diag-action">👉 今日最重要的一件事：{data.recommendation}</div>
        </AiResultCard>
      </div>
    </div>
  );
}
