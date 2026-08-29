import { Button, Card, Col, Row, Table, Tag, message } from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchMenuAnalysis } from "../../api/ops";
import { getErrorMessage } from "../../api/client";
import PageHeader from "../../components/PageHeader";
import type { MenuAnalysis, MenuDish } from "../../types";
import { formatMoney } from "../../utils/format";

const colors: Record<string, string> = {
  明星菜: "red",
  潜力菜: "gold",
  引流菜: "blue",
  淘汰候选: "default",
};

export default function MenuAnalysis() {
  const navigate = useNavigate();
  const [data, setData] = useState<MenuAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMenuAnalysis()
      .then(setData)
      .catch((err) => message.error(getErrorMessage(err, "菜品数据加载失败")))
      .finally(() => setLoading(false));
  }, []);

  const totalSales = (data?.items || []).reduce((sum, item) => sum + item.sales_amount, 0);
  const scatter = {
    tooltip: {
      formatter: (params: { data: { name: string; value: number[] } }) =>
        `${params.data.name}<br/>销量 ${params.data.value[0]}<br/>毛利率 ${params.data.value[1]}%`,
    },
    grid: { left: 56, right: 36, top: 36, bottom: 48 },
    xAxis: { name: "销量", type: "value" },
    yAxis: { name: "毛利率%", type: "value" },
    series: [
      {
        type: "scatter",
        symbolSize: 16,
        data: (data?.items || []).map((item) => ({
          name: item.name,
          value: [item.sales_count, item.gross_margin],
          itemStyle: {
            color:
              item.quadrant === "明星菜"
                ? "#b5453a"
                : item.quadrant === "潜力菜"
                  ? "#c9a227"
                  : item.quadrant === "引流菜"
                    ? "#3b6ea5"
                    : "#9aa0a6",
          },
        })),
        markLine: {
          silent: true,
          symbol: "none",
          lineStyle: { type: "dashed", color: "#9aa0a6" },
          data: [{ xAxis: data?.avg_sales || 0 }, { yAxis: data?.avg_margin || 0 }],
          label: { formatter: "{b}" },
        },
      },
    ],
  };

  return (
    <div>
      <PageHeader
        title="菜品经营分析"
        extra={
          <Button type="primary" onClick={() => navigate("/menu-diagnosis")}>
            AI诊断菜单
          </Button>
        }
      >
        不只看卖得多，还要看毛利高不高。成本为模拟数据，用于演示。
      </PageHeader>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        {Object.entries(data?.counts || {}).map(([name, value]) => (
          <Col span={6} key={name}>
            <Card>
              <StatisticLike title={name} value={value} />
            </Card>
          </Col>
        ))}
      </Row>
      <Card title="销量 × 毛利率 四象限" style={{ marginBottom: 16 }}>
        <p className="demo-note" style={{ marginTop: 0 }}>
          虚线交叉为平均销量 / 平均毛利率：右上明星菜、左上潜力菜、右下引流菜、左下淘汰候选。成本为模拟数据。
        </p>
        <ReactECharts option={scatter} style={{ height: 360 }} />
      </Card>
      <Card>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={data?.items || []}
          columns={[
            { title: "菜品", dataIndex: "name" },
            { title: "分类", dataIndex: "category", width: 90 },
            { title: "销量", dataIndex: "sales_count", width: 80 },
            { title: "销售额", dataIndex: "sales_amount", render: (value) => formatMoney(value) },
            {
              title: "销售占比",
              dataIndex: "sales_amount",
              key: "share",
              width: 90,
              render: (value: number) => (totalSales ? `${((value / totalSales) * 100).toFixed(1)}%` : "-"),
            },
            { title: "售价", dataIndex: "price", render: (value) => formatMoney(value) },
            { title: "成本", dataIndex: "cost_price", render: (value) => formatMoney(value) },
            { title: "毛利", dataIndex: "gross_profit", render: (value) => formatMoney(value) },
            { title: "毛利率", dataIndex: "gross_margin", render: (value) => `${value}%` },
            {
              title: "趋势",
              dataIndex: "sales_trend",
              render: (value: number) => (
                <span style={{ color: value >= 0 ? "#2f6f5e" : "#b5453a" }}>
                  {value >= 0 ? "↑" : "↓"}
                  {Math.abs(value)}%
                </span>
              ),
            },
            {
              title: "象限",
              dataIndex: "quadrant",
              render: (value: string, record: MenuDish) => (
                <Tag color={colors[value]} title={record.advice}>
                  {value}
                </Tag>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}

function StatisticLike({ title, value }: { title: string; value: number }) {
  return (
    <div>
      <div style={{ color: "#6b7280" }}>{title}</div>
      <div style={{ fontSize: 28, fontWeight: 600 }}>{value}</div>
    </div>
  );
}
