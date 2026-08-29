import { Alert, Button, Card, Col, Row, Spin, Statistic, Tag } from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchDashboard } from "../../api/dashboard";
import { getErrorMessage } from "../../api/client";
import PageHeader from "../../components/PageHeader";
import type { DashboardOverview, DiagnosisItem } from "../../types";

const levelMeta: Record<string, { color: string; label: string }> = {
  critical: { color: "red", label: "重点关注" },
  positive: { color: "green", label: "正向增长" },
  opportunity: { color: "gold", label: "经营机会" },
};

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

  if (loading) return <Spin />;
  if (error || !data) return <Alert type="error" showIcon message={error || "暂无数据"} />;

  const trendOption = {
    tooltip: { trigger: "axis" },
    grid: { left: 48, right: 16, top: 24, bottom: 32 },
    xAxis: { type: "category", data: data.trend.map((item) => item.date.slice(5)) },
    yAxis: { type: "value" },
    series: [
      {
        name: "营业额",
        type: "line",
        data: data.trend.map((item) => item.revenue),
        itemStyle: { color: "#b5453a" },
        areaStyle: { color: "rgba(181, 69, 58, 0.08)" },
      },
    ],
  };

  const changeText = (value: number, suffix = "%") => (
    <span style={{ color: value >= 0 ? "#2f6f5e" : "#b5453a", fontSize: 13 }}>
      较昨日 {value >= 0 ? "+" : ""}
      {value}
      {suffix}
    </span>
  );

  return (
    <div>
      <PageHeader title="宴江南 AI老板经营驾驶舱">
        不要自己翻图表。先看 AI 今天发现了什么、最该做什么。
      </PageHeader>
      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <Card className="stat-card">
            <Statistic title="今日营业额" prefix="¥" value={data.today_revenue} precision={0} />
            {changeText(data.revenue_change)}
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card className="stat-card">
            <Statistic title="今日订单数" value={data.today_orders} />
            {changeText(data.order_change)}
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card className="stat-card">
            <Statistic title="客单价" prefix="¥" value={data.average_order_amount} precision={0} />
            {changeText(data.aov_change)}
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card className="stat-card">
            <Statistic title="经营评分" value={data.score} suffix={`/100 ${data.stars_label || ""}`} />
            <span style={{ color: "#6b7280", fontSize: 13 }}>
              预计营业额 ¥{Math.round(data.forecast_revenue || 0)} · 较上周 {data.week_change >= 0 ? "+" : ""}
              {data.week_change}%
            </span>
          </Card>
        </Col>
      </Row>

      <div className="ai-card" style={{ marginTop: 16 }}>
        <h3>AI今日经营诊断</h3>
        <div style={{ color: "#6b7280", marginBottom: 8 }}>
          今天系统发现 {(data.diagnosis || []).length} 个值得关注的问题：
        </div>
        {(data.diagnosis || []).map((item: DiagnosisItem) => (
          <div className="diag-item" key={item.title}>
            <Tag color={levelMeta[item.level]?.color || "default"}>{levelMeta[item.level]?.label || item.level}</Tag>
            <strong style={{ marginLeft: 8 }}>{item.title}</strong>
            <div style={{ marginTop: 6 }}>{item.detail}</div>
            <div style={{ color: "#6b7280", marginTop: 4 }}>可能原因：{item.reason}</div>
            <div style={{ marginTop: 4 }}>
              建议：{item.suggestion}{" "}
              <Button type="link" onClick={() => navigate(item.link)}>
                查看详情
              </Button>
            </div>
          </div>
        ))}
        <div className="diag-action">👉 今日最重要：{data.recommendation || "重点推广家庭聚餐套餐"}</div>
      </div>

      <Card
        title="AI经营机会"
        extra={<Button type="link" onClick={() => navigate("/opportunities")}>查看全部机会</Button>}
        style={{ marginTop: 16 }}
      >
        {(data.top_opportunities || []).length ? (
          (data.top_opportunities || []).map((item) => (
            <div
              className="diag-item"
              key={item.id}
              style={{ cursor: "pointer" }}
              onClick={() => navigate("/opportunities")}
            >
              <Tag color={item.level === "high" ? "red" : item.level === "medium" ? "orange" : "green"}>
                {item.level_label}
              </Tag>
              <strong style={{ marginLeft: 8 }}>{item.title}</strong>
              <span style={{ color: "#6b7280", marginLeft: 8 }}>优先级 {item.priority}</span>
            </div>
          ))
        ) : (
          <div>
            还没有生成今日机会。
            <Button type="link" onClick={() => navigate("/opportunities")}>
              去机会中心生成
            </Button>
          </div>
        )}
      </Card>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24} lg={10}>
          <Card title="菜品经营" extra={<Button type="link" onClick={() => navigate("/menu-analysis")}>查看</Button>}>
            {Object.entries(data.menu_counts || {}).map(([name, value]) => (
              <div key={name} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                <span>{name}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </Card>
        </Col>
        <Col xs={24} lg={14}>
          <Card title="营业趋势">
            <ReactECharts option={trendOption} style={{ height: 220 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card
            hoverable
            onClick={() => navigate("/customer-recall")}
            title="客户经营"
          >
            待召回 {data.high_value_sleeping_count} 人
          </Card>
        </Col>
        <Col span={8}>
          <Card hoverable onClick={() => navigate("/banquet-leads")} title="宴请客户">
            待跟进 {data.banquet_pending_count} 人
          </Card>
        </Col>
        <Col span={8}>
          <Card hoverable onClick={() => navigate("/staff-assistant")} title="AI员工助手">
            今日推荐高毛利菜
          </Card>
        </Col>
      </Row>
    </div>
  );
}
