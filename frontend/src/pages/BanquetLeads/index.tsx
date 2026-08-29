import {
  Button,
  Card,
  DatePicker,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Table,
  message,
} from "antd";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import {
  analyzeBanquetLead,
  createBanquetLead,
  fetchBanquetLeads,
  updateBanquetLead,
} from "../../api/banquet";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader, { CopyButton } from "../../components/PageHeader";
import type { BanquetAnalyzeResult, BanquetLeadItem } from "../../types";
import { riskColor } from "../../utils/format";

const EVENT_TYPES = ["生日宴", "家庭聚餐", "商务宴请", "公司团建", "同学聚会", "婚宴", "寿宴", "公司聚餐"];
const STATUSES = ["待跟进", "已联系", "已报价", "已确定", "已流失", "已完成"];
const SOURCES = ["微信", "电话", "到店咨询", "老客户介绍", "美团"];

export default function BanquetLeads() {
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<BanquetLeadItem[]>([]);
  const [status, setStatus] = useState<string>();
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm();
  const [current, setCurrent] = useState<BanquetLeadItem | null>(null);
  const [analysis, setAnalysis] = useState<BanquetAnalyzeResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const load = async (nextStatus = status) => {
    setLoading(true);
    try {
      const data = await fetchBanquetLeads(nextStatus);
      setItems(data.items);
    } catch (error) {
      message.error(getErrorMessage(error, "宴请线索加载失败"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <PageHeader
        title="宴请客户"
        extra={
          <Button type="primary" onClick={() => setCreateOpen(true)}>
            新建线索
          </Button>
        }
      >
        高客单价客户经营：把生日宴、公司聚餐、商务宴请单独跟进起来。
      </PageHeader>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Select
            allowClear
            placeholder="按状态筛选"
            style={{ width: 180 }}
            options={STATUSES.map((item) => ({ value: item, label: item }))}
            value={status}
            onChange={(value) => {
              setStatus(value);
              void load(value);
            }}
          />
        </Space>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={items}
          columns={[
            { title: "客户", dataIndex: "customer_name" },
            { title: "宴请类型", dataIndex: "event_type" },
            { title: "人数", dataIndex: "people_count", render: (value) => `${value}人` },
            { title: "预计金额", dataIndex: "expected_amount", render: (value) => `¥${value}` },
            { title: "活动时间", dataIndex: "event_date" },
            { title: "来源", dataIndex: "source" },
            {
              title: "当前状态",
              dataIndex: "status",
              render: (value, record) => (
                <Select
                  size="small"
                  value={value}
                  style={{ width: 110 }}
                  options={STATUSES.map((item) => ({ value: item, label: item }))}
                  onChange={async (next) => {
                    try {
                      await updateBanquetLead(record.id, { status: next });
                      message.success("状态已更新");
                      void load();
                    } catch (error) {
                      message.error(getErrorMessage(error, "状态更新失败"));
                    }
                  }}
                />
              ),
            },
            {
              title: "操作",
              render: (_, record) => (
                <Button
                  type="primary"
                  onClick={async () => {
                    setCurrent(record);
                    setAnalysis(null);
                    setDrawerOpen(true);
                    setAnalyzing(true);
                    try {
                      setAnalysis(await analyzeBanquetLead(record.id));
                    } catch (error) {
                      message.error(AI_UNAVAILABLE);
                      console.error(error);
                    } finally {
                      setAnalyzing(false);
                    }
                  }}
                >
                  AI分析
                </Button>
              ),
            },
          ]}
        />
      </Card>
      <Drawer
        title={current ? `${current.customer_name} · 宴请线索分析` : "AI分析"}
        width={520}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        {analyzing ? <div>正在分析线索...</div> : null}
        {analysis ? (
          <AiResultCard demoFallback={analysis.demo_fallback}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="客户价值">{analysis.customer_value}</Descriptions.Item>
              <Descriptions.Item label="成交潜力">
                <span style={{ color: riskColor(analysis.deal_potential === "高" ? "高" : analysis.deal_potential), fontWeight: 600 }}>
                  {analysis.deal_potential}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="原因">{analysis.reason}</Descriptions.Item>
              <Descriptions.Item label="跟进建议">{analysis.followup_suggestion}</Descriptions.Item>
              <Descriptions.Item label="下一步">{analysis.next_step}</Descriptions.Item>
            </Descriptions>
            <h4>建议跟进话术</h4>
            <div className="copy-block">{analysis.script}</div>
            <div style={{ marginTop: 8 }}>
              <CopyButton text={analysis.script} />
            </div>
          </AiResultCard>
        ) : null}
      </Drawer>
      <Modal
        title="新建宴请线索"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ event_type: "公司聚餐", source: "微信", status: "待跟进", people_count: 25, expected_amount: "5000-8000" }}
          onFinish={async (values) => {
            try {
              await createBanquetLead({
                ...values,
                event_date: values.event_date ? dayjs(values.event_date).format("YYYY-MM-DD") : null,
              });
              message.success("线索已创建");
              setCreateOpen(false);
              form.resetFields();
              void load();
            } catch (error) {
              message.error(getErrorMessage(error, "创建失败"));
            }
          }}
        >
          <Form.Item name="customer_name" label="客户" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="手机" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="event_type" label="宴请类型" rules={[{ required: true }]}>
            <Select options={EVENT_TYPES.map((item) => ({ value: item, label: item }))} />
          </Form.Item>
          <Form.Item name="people_count" label="人数" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="expected_amount" label="预计金额" rules={[{ required: true }]}>
            <Input placeholder="例如 5000-8000" />
          </Form.Item>
          <Form.Item name="event_date" label="活动时间">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="source" label="来源">
            <Select options={SOURCES.map((item) => ({ value: item, label: item }))} />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
