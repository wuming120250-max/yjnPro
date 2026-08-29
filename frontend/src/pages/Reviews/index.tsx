import { Alert, Button, Card, Col, Rate, Row, Space, Statistic, Table, Tag, message } from "antd";
import { useEffect, useState } from "react";
import { analyzeReviews, fetchReviews } from "../../api/reviews";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader from "../../components/PageHeader";
import type { ReviewAnalyzeResult, ReviewItem } from "../../types";

export default function Reviews() {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [total, setTotal] = useState(0);
  const [average, setAverage] = useState(0);
  const [positive, setPositive] = useState(0);
  const [negative, setNegative] = useState(0);
  const [result, setResult] = useState<ReviewAnalyzeResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchReviews()
      .then((data) => {
        setItems(data.items);
        setTotal(data.total);
        setAverage(data.average_rating);
        setPositive(data.positive_rate);
        setNegative(data.negative_rate);
      })
      .catch((err) => setError(getErrorMessage(err, "评价加载失败")))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="AI评价分析"
        extra={
          <Button
            type="primary"
            loading={analyzing}
            onClick={async () => {
              setAnalyzing(true);
              try {
                setResult(await analyzeReviews());
              } catch (err) {
                message.error(AI_UNAVAILABLE);
                console.error(err);
              } finally {
                setAnalyzing(false);
              }
            }}
          >
            AI分析全部评价
          </Button>
        }
      >
        看客户喜欢什么、不满意什么，并生成经营建议。
      </PageHeader>
      {error ? <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} /> : null}
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="评价总数" value={total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="平均评分" value={average} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="好评率" value={`${positive}%`} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="差评率" value={`${negative}%`} />
          </Card>
        </Col>
      </Row>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <AiResultCard demoFallback={result.demo_fallback}>
            <Row gutter={24}>
              <Col span={12}>
                <h4>客户最喜欢</h4>
                <ol>
                  {result.likes.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
                <h4>客户主要抱怨</h4>
                <ol>
                  {result.complaints.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </Col>
              <Col span={12}>
                <h4>客户最关注</h4>
                <Space wrap>
                  {result.focus.map((item) => (
                    <Tag key={item}>{item}</Tag>
                  ))}
                </Space>
                <h4 style={{ marginTop: 16 }}>高频菜品</h4>
                <Space wrap>
                  {result.hot_dishes.map((item) => (
                    <Tag color="gold" key={item}>
                      {item}
                    </Tag>
                  ))}
                </Space>
                <h4 style={{ marginTop: 16 }}>高频场景</h4>
                <Space wrap>
                  {result.hot_scenes.map((item) => (
                    <Tag color="red" key={item}>
                      {item}
                    </Tag>
                  ))}
                </Space>
              </Col>
            </Row>
            <h4>AI经营建议</h4>
            {result.suggestions.map((item) => (
              <div key={item.finding} className="insight-item">
                <div>{item.finding}</div>
                <div style={{ color: "#6b7280", marginTop: 4 }}>建议：{item.suggestion}</div>
              </div>
            ))}
          </AiResultCard>
        </div>
      ) : null}
      <Card title="评价列表" style={{ marginTop: 16 }}>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={items}
          columns={[
            { title: "客户", dataIndex: "customer_name", width: 100 },
            {
              title: "评分",
              dataIndex: "rating",
              width: 160,
              render: (value) => <Rate disabled value={value} />,
            },
            { title: "内容", dataIndex: "content" },
            { title: "来源", dataIndex: "source", width: 100 },
            {
              title: "情感",
              dataIndex: "sentiment",
              width: 90,
              render: (value) => (
                <Tag color={value === "好评" ? "green" : value === "差评" ? "red" : "default"}>{value}</Tag>
              ),
            },
            { title: "日期", dataIndex: "review_date", width: 120 },
          ]}
        />
      </Card>
    </div>
  );
}
