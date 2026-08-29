import { Button, Card, Descriptions, Drawer, Space, Table, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { analyzeRecallCustomer, fetchRecallCustomers, generateRecallMessage } from "../../api/recall";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader, { CopyButton } from "../../components/PageHeader";
import type { RecallAnalyzeResult, RecallCustomerItem } from "../../types";
import { formatMoney, levelColor, riskColor } from "../../utils/format";

export default function CustomerRecall() {
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<RecallCustomerItem[]>([]);
  const [count, setCount] = useState(0);
  const [current, setCurrent] = useState<RecallCustomerItem | null>(null);
  const [open, setOpen] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<RecallAnalyzeResult | null>(null);
  const [script, setScript] = useState("");
  const [scriptLoading, setScriptLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchRecallCustomers()
      .then((data) => {
        setItems(data.items);
        setCount(data.high_value_sleeping_count);
      })
      .catch((error) => message.error(getErrorMessage(error, "召回客户加载失败")))
      .finally(() => setLoading(false));
  }, []);

  const openAnalyze = async (record: RecallCustomerItem) => {
    setCurrent(record);
    setOpen(true);
    setAnalysis(null);
    setScript("");
    setAnalyzing(true);
    try {
      const result = await analyzeRecallCustomer(record.id);
      setAnalysis(result);
    } catch (error) {
      message.error(AI_UNAVAILABLE);
      console.error(error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <PageHeader title="AI客户召回">
        系统发现：{count} 名高价值客户长期未到店。预计可重点召回：{count} 人
      </PageHeader>
      <Card>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={items}
          pagination={false}
          columns={[
            { title: "客户", dataIndex: "customer_name" },
            { title: "消费次数", dataIndex: "total_orders", render: (value) => `${value}次` },
            { title: "累计消费", dataIndex: "total_amount", render: (value) => formatMoney(value) },
            { title: "最近消费", dataIndex: "sleep_days", render: (value) => `${value}天未消费` },
            {
              title: "客户标签",
              dataIndex: "tag_list",
              render: (tags: string[]) => tags.map((tag) => <Tag key={tag}>{tag}</Tag>),
            },
            {
              title: "召回优先级",
              dataIndex: "recall_priority_label",
              render: (value, record) => (
                <span style={{ color: record.recall_priority >= 5 ? "#b5453a" : "#c9a227" }}>{value}</span>
              ),
            },
            {
              title: "操作",
              render: (_, record) => (
                <Button type="primary" onClick={() => void openAnalyze(record)}>
                  AI分析
                </Button>
              ),
            },
          ]}
        />
      </Card>
      <Drawer
        title={current ? `${current.customer_name} · AI客户分析` : "AI客户分析"}
        width={560}
        open={open}
        onClose={() => setOpen(false)}
      >
        {current ? (
          <Descriptions size="small" column={1} style={{ marginBottom: 16 }}>
            <Descriptions.Item label="消费次数">{current.total_orders}次</Descriptions.Item>
            <Descriptions.Item label="累计消费">{formatMoney(current.total_amount)}</Descriptions.Item>
            <Descriptions.Item label="最近消费">{current.sleep_days}天未消费</Descriptions.Item>
            <Descriptions.Item label="客户等级">
              <Tag color={levelColor(current.customer_level)}>{current.customer_level}</Tag>
            </Descriptions.Item>
          </Descriptions>
        ) : null}
        {analyzing ? <Typography.Paragraph>正在分析客户...</Typography.Paragraph> : null}
        {analysis ? (
          <AiResultCard demoFallback={analysis.demo_fallback}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="客户价值">{analysis.customer_value}</Descriptions.Item>
              <Descriptions.Item label="客户状态">{analysis.customer_status}</Descriptions.Item>
              <Descriptions.Item label="流失风险">
                <span style={{ color: riskColor(analysis.churn_risk), fontWeight: 600 }}>
                  {analysis.churn_risk}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="AI判断">{analysis.judgment}</Descriptions.Item>
              <Descriptions.Item label="召回建议">{analysis.recall_suggestion}</Descriptions.Item>
              <Descriptions.Item label="推荐营销方式">{analysis.recommended_channel}</Descriptions.Item>
            </Descriptions>
            <Space direction="vertical" style={{ width: "100%", marginTop: 16 }} size="middle">
              <Button
                type="primary"
                loading={scriptLoading}
                onClick={async () => {
                  if (!current) return;
                  setScriptLoading(true);
                  try {
                    const result = await generateRecallMessage(current.id);
                    setScript(result.message);
                  } catch (error) {
                    message.error(AI_UNAVAILABLE);
                    console.error(error);
                  } finally {
                    setScriptLoading(false);
                  }
                }}
              >
                生成微信召回话术
              </Button>
              {script ? (
                <div>
                  <div className="copy-block">{script}</div>
                  <div style={{ marginTop: 8 }}>
                    <CopyButton text={script} />
                  </div>
                </div>
              ) : null}
            </Space>
          </AiResultCard>
        ) : null}
      </Drawer>
    </div>
  );
}
