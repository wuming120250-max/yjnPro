import { Button, Card, Col, Form, InputNumber, Row, Select, Switch, message } from "antd";
import { useState } from "react";
import { recommendDishes } from "../../api/ops";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import AiResultCard from "../../components/AiResultCard";
import PageHeader, { CopyButton } from "../../components/PageHeader";

const SCENES = ["家庭聚餐", "商务宴请", "生日宴", "朋友聚餐", "普通用餐"];
const MODES = ["普通推荐", "高毛利推荐", "招牌菜推荐", "家庭聚餐", "商务宴请", "生日宴"];

export default function StaffAssistant() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, any> | null>(null);

  return (
    <div>
      <PageHeader title="AI员工推荐菜助手">
        给服务员用的：把高毛利、高价值菜卖出去。不是给老板聊天。
      </PageHeader>
      <Row gutter={16}>
        <Col xs={24} lg={9}>
          <Card title="顾客情况">
            <Form
              layout="vertical"
              initialValues={{
                people: 4,
                budget: 500,
                scene: "家庭聚餐",
                taste: "正常",
                first_visit: true,
                mode: "家庭聚餐",
              }}
              onFinish={async (values) => {
                setLoading(true);
                try {
                  setResult(await recommendDishes(values));
                } catch (error) {
                  message.error(getErrorMessage(error, AI_UNAVAILABLE));
                } finally {
                  setLoading(false);
                }
              }}
            >
              <Form.Item name="people" label="人数" rules={[{ required: true }]}>
                <InputNumber min={1} max={20} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="budget" label="预算（元）" rules={[{ required: true }]}>
                <InputNumber min={100} step={50} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="scene" label="场景">
                <Select options={SCENES.map((item) => ({ value: item, label: item }))} />
              </Form.Item>
              <Form.Item name="mode" label="推荐模式">
                <Select options={MODES.map((item) => ({ value: item, label: item }))} />
              </Form.Item>
              <Form.Item name="taste" label="口味">
                <Select
                  options={["正常", "清淡", "偏辣", "少油"].map((item) => ({ value: item, label: item }))}
                />
              </Form.Item>
              <Form.Item name="first_visit" label="第一次来" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                AI推荐
              </Button>
            </Form>
          </Card>
        </Col>
        <Col xs={24} lg={15}>
          {result ? (
            <AiResultCard title="推荐方案" demoFallback={Boolean(result.demo_fallback)}>
              <h4>推荐套餐</h4>
              <ol>
                {(result.dishes || []).map((item: string | { name?: string }, index: number) => {
                  const name = typeof item === "string" ? item : item?.name || JSON.stringify(item);
                  return <li key={`${name}-${index}`}>{name}</li>;
                })}
              </ol>
              <p>
                预计消费：¥{result.estimated_min}～{result.estimated_max}
              </p>
              <p>{result.reason}</p>
              <h4>服务员推荐话术</h4>
              <div className="copy-block">{result.script}</div>
              <div style={{ marginTop: 8 }}>
                <CopyButton text={String(result.script || "")} />
              </div>
            </AiResultCard>
          ) : (
            <Card>输入人数、场景和预算后，点击 AI 推荐。</Card>
          )}
        </Col>
      </Row>
    </div>
  );
}
