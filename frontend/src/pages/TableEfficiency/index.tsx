import { Alert, Button, Card, Col, Row, Table, Tag } from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";
import { analyzeTableEfficiency, fetchTableEfficiency } from "../../api/ops";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader from "../../components/PageHeader";
import { formatMoney } from "../../utils/format";

export default function TableEfficiency() {
  const [data, setData] = useState<Record<string, any> | null>(null);
  const [result, setResult] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchTableEfficiency()
      .then(setData)
      .catch((err) => setError(getErrorMessage(err, "翻台数据加载失败")));
  }, []);

  const slots = data?.slots || [];
  const option = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: slots.map((item: { label: string }) => item.label) },
    yAxis: { type: "value", name: "分钟" },
    series: [
      {
        name: "平均用餐时间",
        type: "bar",
        data: slots.map((item: { avg_duration: number; is_abnormal: boolean }) => ({
          value: item.avg_duration,
          itemStyle: { color: item.is_abnormal ? "#b5453a" : "#c9a227" },
        })),
      },
    ],
  };

  return (
    <div>
      <PageHeader
        title="翻台效率分析"
        extra={
          <Button
            type="primary"
            loading={analyzing}
            onClick={async () => {
              setAnalyzing(true);
              try {
                setResult(await analyzeTableEfficiency());
              } catch (err) {
                setError(getErrorMessage(err, AI_UNAVAILABLE));
              } finally {
                setAnalyzing(false);
              }
            }}
          >
            AI效率诊断
          </Button>
        }
      >
        看高峰期桌台转得快不快。
      </PageHeader>
      <p className="demo-note">{data?.note}</p>
      {error ? <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} /> : null}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <div>高峰时段</div>
            <div style={{ fontSize: 22, fontWeight: 600 }}>{data?.peak?.label || "-"}</div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div>平均用餐</div>
            <div style={{ fontSize: 22, fontWeight: 600 }}>{data?.peak?.avg_duration || 0} 分钟</div>
            {data?.peak?.is_abnormal ? <Tag color="red">高峰期效率异常</Tag> : <Tag>正常</Tag>}
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div>正常水平</div>
            <div style={{ fontSize: 22, fontWeight: 600 }}>{data?.normal_duration || 72} 分钟</div>
          </Card>
        </Col>
      </Row>
      <Card title="各时段平均用餐时间">
        <ReactECharts option={option} style={{ height: 280 }} />
      </Card>
      <Card title="时段明细" style={{ marginTop: 16 }}>
        <Table
          rowKey="label"
          dataSource={slots}
          pagination={false}
          columns={[
            { title: "时段", dataIndex: "label" },
            { title: "桌台数", dataIndex: "table_count" },
            { title: "翻台次数", dataIndex: "turnover" },
            { title: "平均用餐", dataIndex: "avg_duration", render: (value) => `${value}分钟` },
            { title: "营业额", dataIndex: "revenue", render: (value) => formatMoney(value) },
            {
              title: "状态",
              dataIndex: "is_abnormal",
              render: (value) => (value ? <Tag color="red">异常</Tag> : <Tag>正常</Tag>),
            },
          ]}
        />
      </Card>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <AiResultCard title="AI效率诊断" demoFallback={Boolean(result.demo_fallback)}>
            <p>{result.verdict}</p>
            <p>{result.peak_issue}</p>
            <ol>
              {(result.suggestions || []).map((item: string) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
          </AiResultCard>
        </div>
      ) : null}
    </div>
  );
}
