import { Alert, Button, Card, Col, Row, Statistic, Tag } from "antd";
import type { OpportunityListResponse } from "../../types";

export default function OpportunityStats({
  stats,
  bizDate,
  demoMode,
}: {
  stats: OpportunityListResponse["stats"];
  bizDate: string;
  demoMode: boolean;
}) {
  return (
    <div>
      {demoMode ? (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message="当前为演示模式，数据为模拟数据"
        />
      ) : (
        <p className="demo-note" style={{ marginTop: 0 }}>
          翻台、菜品成本等为演示模拟数据，影响金额为估算。
        </p>
      )}
      <div style={{ marginBottom: 12, color: "#6b7280" }}>
        {bizDate} · AI 今天为您发现 {stats.total} 个经营机会
      </div>
      <Row gutter={16}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="全部机会" value={stats.total} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="高优先级" value={stats.high} prefix={<Tag color="red">高</Tag>} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="中优先级" value={stats.medium} prefix={<Tag color="orange">中</Tag>} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="已完成" value={stats.completed} prefix={<Tag>完成</Tag>} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
