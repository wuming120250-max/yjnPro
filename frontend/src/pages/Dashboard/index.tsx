import {
  Alert,
  Button,
  Card,
  Col,
  Row,
  Space,
  Spin,
  Statistic,
  Tag,
} from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchDashboard } from "../../api/dashboard";
import { getErrorMessage } from "../../api/client";
import PageHeader from "../../components/PageHeader";
import type { DashboardOverview } from "../../types";

export default function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard()
      .then(setData)
      .catch((err) => setError(getErrorMessage(err, "经营数据加载失败")))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Spin />;
  }
  if (error || !data) {
    return <Alert type="error" showIcon message={error || "暂无数据"} />;
  }

  const trendOption = {
    tooltip: { trigger: "axis" },
    grid: { left: 48, right: 16, top: 24, bottom: 32 },
    xAxis: {
      type: "category",
      data: data.trend.map((item) => item.date.slice(5)),
    },
    yAxis: { type: "value" },
    series: [
      {
        name: "营业额",
        type: "line",
        smooth: true,
        data: data.trend.map((item) => item.revenue),
        itemStyle: { color: "#b5453a" },
        areaStyle: { color: "rgba(181, 69, 58, 0.08)" },
      },
    ],
  };

  const pieOption = {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        type: "pie",
        radius: ["42%", "68%"],
        data: Object.entries(data.level_distribution).map(([name, value]) => ({ name, value })),
      },
    ],
  };

  return (
    <div>
      <PageHeader title="AI经营驾驶舱">今天应该做什么：看经营数据、看 AI 发现、直接执行动作。</PageHeader>
      <Row gutter={[16, 16]}>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="今日营业额" prefix="¥" value={data.today_revenue} precision={0} />
          </Card>
        </Col>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="今日订单数" value={data.today_orders} />
          </Card>
        </Col>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="今日客单价" prefix="¥" value={data.average_order_amount} precision={0} />
          </Card>
        </Col>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="客户总数" value={data.customer_count} />
          </Card>
        </Col>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="老客户占比" suffix="%" value={data.old_customer_rate} />
          </Card>
        </Col>
        <Col xs={12} md={8} xl={4}>
          <Card className="stat-card">
            <Statistic title="待跟进客户" suffix="人" value={data.pending_followups} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <div className="ai-card">
            <h3>AI今日发现</h3>
            {data.insights.map((item) => (
              <div className="insight-item" key={item.title}>
                <Space>
                  <Tag color={item.level === "success" ? "green" : "orange"}>
                    {item.level === "success" ? "机会" : "提醒"}
                  </Tag>
                  <strong>{item.title}</strong>
                </Space>
                <div style={{ marginTop: 6, color: "#6b7280" }}>{item.suggestion}</div>
              </div>
            ))}
          </div>
          <Card title="今日行动" style={{ marginTop: 16 }}>
            <Space wrap size="middle">
              <Button type="primary" onClick={() => navigate("/customer-recall")}>
                召回沉睡客户
              </Button>
              <Button onClick={() => navigate("/marketing")}>生成营销方案</Button>
              <Button onClick={() => navigate("/reviews")}>分析客户评价</Button>
              <Button onClick={() => navigate("/banquet-leads")}>查看宴请客户</Button>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="近7日营业额">
            <ReactECharts option={trendOption} style={{ height: 240 }} />
          </Card>
        </Col>
      </Row>
      <Card title="客户分层" style={{ marginTop: 16 }}>
        <ReactECharts option={pieOption} style={{ height: 280 }} />
      </Card>
    </div>
  );
}
