import { Button, Card, Col, Form, Input, Row, Select, Space, message } from "antd";
import { useState } from "react";
import { generateMarketingPlan } from "../../api/marketing";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader, { CopyButton } from "../../components/PageHeader";
import type { MarketingPlan } from "../../types";

const GOALS = ["老客户召回", "新客引流", "家庭聚餐", "生日宴", "商务宴请", "节日营销", "周末营销"];

export default function Marketing() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<MarketingPlan | null>(null);

  return (
    <div>
      <PageHeader title="AI营销助手">填写目标和活动信息，AI 生成可直接使用的营销方案与文案。</PageHeader>
      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card title="活动信息">
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                goal: "家庭聚餐",
                dish: "特色海鲜",
                promotion: "消费满388元赠特色菜",
                target_customer: "25-45岁家庭客户",
                date_range: "本周末",
              }}
              onFinish={async (values) => {
                setLoading(true);
                try {
                  const result = await generateMarketingPlan(values);
                  setPlan(result);
                } catch (error) {
                  message.error(getErrorMessage(error, AI_UNAVAILABLE));
                } finally {
                  setLoading(false);
                }
              }}
            >
              <Form.Item name="goal" label="营销目标" rules={[{ required: true }]}>
                <Select options={GOALS.map((item) => ({ value: item, label: item }))} />
              </Form.Item>
              <Form.Item name="dish" label="本次主推菜品" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="promotion" label="活动优惠" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="target_customer" label="目标客户">
                <Input />
              </Form.Item>
              <Form.Item name="date_range" label="活动时间">
                <Input />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                AI生成营销方案
              </Button>
            </Form>
          </Card>
        </Col>
        <Col xs={24} lg={14}>
          {plan ? (
            <AiResultCard title="营销方案" demoFallback={plan.demo_fallback}>
              <Space direction="vertical" size="large" style={{ width: "100%" }}>
                <section>
                  <h4>营销主题</h4>
                  <div>{plan.theme}</div>
                </section>
                <section>
                  <h4>目标客户</h4>
                  <div>{plan.target_customer}</div>
                </section>
                <section>
                  <h4>营销策略</h4>
                  <div>{plan.strategy}</div>
                </section>
                <section>
                  <h4>活动建议</h4>
                  <div>{plan.activity_suggestion}</div>
                </section>
                <CopySection title="朋友圈文案" text={plan.moments_copy} />
                <CopySection title="微信群文案" text={plan.wechat_group_copy} />
                <CopySection title="服务员推荐话术" text={plan.staff_script} />
                <CopySection title="大众点评宣传文案" text={plan.dianping_copy} />
              </Space>
            </AiResultCard>
          ) : (
            <Card>填写左侧信息后，点击生成营销方案。</Card>
          )}
        </Col>
      </Row>
    </div>
  );
}

function CopySection({ title, text }: { title: string; text: string }) {
  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h4 style={{ margin: 0 }}>{title}</h4>
        <CopyButton text={text} />
      </div>
      <div className="copy-block" style={{ marginTop: 8 }}>
        {text}
      </div>
    </section>
  );
}
