import { Alert, Button, Card, Col, Row, Space, Tag } from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";
import { analyzeRevenue, fetchRevenueAnalysis } from "../../api/ops";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader from "../../components/PageHeader";
import { formatMoney } from "../../utils/format";

export default function RevenueAnalysis() {
  const [metrics, setMetrics] = useState<Record<string, any> | null>(null);
  const [result, setResult] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [range, setRange] = useState<"7" | "30">("30");

  useEffect(() => {
    fetchRevenueAnalysis()
      .then(setMetrics)
      .catch((err) => setError(getErrorMessage(err, "营业数据加载失败")))
      .finally(() => setLoading(false));
  }, []);

  const items = (metrics?.items || []) as { date: string; revenue: number; order_count: number; average_order_amount: number }[];
  const chartItems = range === "7" ? items.slice(-7) : items;
  const worstDate = metrics?.worst_day?.date;
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: ["营业额", "订单数"] },
    grid: { left: 56, right: 48, top: 32, bottom: 32 },
    xAxis: { type: "category", data: chartItems.map((item) => item.date.slice(5)) },
    yAxis: [{ type: "value", name: "营业额" }, { type: "value", name: "订单" }],
    series: [
      {
        name: "营业额",
        type: "line",
        data: chartItems.map((item) => item.revenue),
        itemStyle: { color: "#b5453a" },
        markPoint: worstDate
          ? {
              data: [{ name: "异常低点", coord: [worstDate.slice(5), metrics?.worst_day?.revenue], value: "异常" }],
            }
          : undefined,
      },
      {
        name: "订单数",
        type: "bar",
        yAxisIndex: 1,
        data: chartItems.map((item) => item.order_count),
        itemStyle: { color: "#c9a227" },
      },
    ],
  };

  return (
    <div>
      <PageHeader
        title="AI营业异常分析"
        extra={
          <Button
            type="primary"
            loading={analyzing}
            onClick={async () => {
              setAnalyzing(true);
              try {
                setResult(await analyzeRevenue());
              } catch (err) {
                setError(getErrorMessage(err, AI_UNAVAILABLE));
              } finally {
                setAnalyzing(false);
              }
            }}
          >
            AI分析原因
          </Button>
        }
      >
        用同比、环比和阈值发现异常，再让 AI 解释原因。数据为演示模拟数据。
      </PageHeader>
      {loading && !metrics ? <Alert type="info" showIcon message="营业数据加载中…" style={{ marginBottom: 16 }} /> : null}
      {metrics?.is_anomaly ? (
        <Alert
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          message={`${metrics?.worst_day?.date} 营业额较近7日平均下降 ${Math.abs(metrics?.worst_drop || 0)}%，系统判定为营业额异常下降。`}
          description="客单价变化不大，重点看晚餐客流和家庭聚餐订单。点击「AI分析原因」看建议。"
        />
      ) : null}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <div style={{ color: "#6b7280" }}>今日营业额</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{formatMoney(metrics?.today?.revenue || 0)}</div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ color: "#6b7280" }}>过去7日平均</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{formatMoney(metrics?.avg7 || 0)}</div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ color: "#6b7280" }}>最低一天</div>
            <div style={{ fontSize: 22, fontWeight: 600 }}>{formatMoney(metrics?.worst_day?.revenue || 0)}</div>
            <div style={{ color: "#6b7280" }}>{metrics?.worst_day?.date}</div>
            {metrics?.is_anomaly ? <Tag color="red">营业额异常下降 {Math.abs(metrics?.worst_drop || 0)}%</Tag> : <Tag color="green">波动正常</Tag>}
          </Card>
        </Col>
      </Row>
      <Card
        title="营业额趋势"
        extra={
          <Space>
            <Button size="small" type={range === "7" ? "primary" : "default"} onClick={() => setRange("7")}>
              近7天
            </Button>
            <Button size="small" type={range === "30" ? "primary" : "default"} onClick={() => setRange("30")}>
              近30天
            </Button>
          </Space>
        }
      >
        <ReactECharts option={option} style={{ height: 320 }} />
      </Card>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <AiResultCard title="AI营业异常分析" demoFallback={Boolean(result.demo_fallback)}>
            <p>{result.verdict}</p>
            <p>
              <strong>主要原因：</strong>
              {result.main_reason}
            </p>
            <ol>
              {(result.reasons || []).map((item: string) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
            <p>判断：{result.traffic_or_ticket}；影响最大时间段：{result.key_period}；客群：{result.key_customer}</p>
            <div className="diag-action">👉 {result.tomorrow_action}</div>
          </AiResultCard>
        </div>
      ) : null}
    </div>
  );
}
