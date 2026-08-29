import { Button, Card, Descriptions, Drawer, Input, Select, Space, Table, Tag, message } from "antd";
import { useEffect, useState } from "react";
import { fetchCustomer, fetchCustomers } from "../../api/customers";
import { getErrorMessage } from "../../api/client";
import PageHeader from "../../components/PageHeader";
import type { CustomerDetail, CustomerItem } from "../../types";
import { formatMoney, levelColor } from "../../utils/format";

const LEVELS = ["高价值沉睡客户", "高价值客户", "沉睡客户", "潜力客户", "普通客户"];

export default function Customers() {
  const [keyword, setKeyword] = useState("");
  const [level, setLevel] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<CustomerItem[]>([]);
  const [detail, setDetail] = useState<CustomerDetail | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const load = async (nextPage = page) => {
    setLoading(true);
    try {
      const data = await fetchCustomers({ keyword, level, page: nextPage, page_size: 10 });
      setItems(data.items);
      setTotal(data.total);
    } catch (error) {
      message.error(getErrorMessage(error, "客户列表加载失败"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <PageHeader title="客户管理">查看客户消费、标签和分层，识别高价值与沉睡客户。</PageHeader>
      <Card>
        <Space wrap style={{ marginBottom: 16 }}>
          <Input.Search
            allowClear
            placeholder="搜索姓名或手机号"
            style={{ width: 240 }}
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            onSearch={() => {
              setPage(1);
              void load(1);
            }}
          />
          <Select
            allowClear
            placeholder="客户等级"
            style={{ width: 180 }}
            value={level}
            options={LEVELS.map((item) => ({ value: item, label: item }))}
            onChange={(value) => {
              setLevel(value);
              setPage(1);
            }}
          />
          <Button
            type="primary"
            onClick={() => {
              setPage(1);
              void load(1);
            }}
          >
            筛选
          </Button>
        </Space>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={items}
          pagination={{
            current: page,
            total,
            pageSize: 10,
            onChange: (next) => {
              setPage(next);
              void load(next);
            },
          }}
          columns={[
            { title: "客户", dataIndex: "customer_name" },
            { title: "消费次数", dataIndex: "total_orders", render: (value) => `${value}次` },
            { title: "累计消费", dataIndex: "total_amount", render: (value) => formatMoney(value) },
            {
              title: "最近消费",
              dataIndex: "sleep_days",
              render: (value, record) => `${value}天前（${record.last_order_date || "-"}）`,
            },
            { title: "平均客单", dataIndex: "average_order_amount", render: (value) => formatMoney(value) },
            {
              title: "客户等级",
              dataIndex: "customer_level",
              render: (value) => <Tag color={levelColor(value)}>{value}</Tag>,
            },
            {
              title: "客户标签",
              dataIndex: "tag_list",
              render: (tags: string[]) => tags.map((tag) => <Tag key={tag}>{tag}</Tag>),
            },
            {
              title: "操作",
              render: (_, record) => (
                <Button
                  type="link"
                  onClick={async () => {
                    try {
                      const data = await fetchCustomer(record.id);
                      setDetail(data);
                      setDetailOpen(true);
                    } catch (error) {
                      message.error(getErrorMessage(error, "客户详情加载失败"));
                    }
                  }}
                >
                  查看
                </Button>
              ),
            },
          ]}
        />
      </Card>
      <Drawer title="客户详情" width={640} open={detailOpen} onClose={() => setDetailOpen(false)}>
        {detail ? (
          <>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="客户">{detail.customer_name}</Descriptions.Item>
              <Descriptions.Item label="手机">{detail.phone}</Descriptions.Item>
              <Descriptions.Item label="等级">
                <Tag color={levelColor(detail.customer_level)}>{detail.customer_level}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="标签">{detail.tags}</Descriptions.Item>
              <Descriptions.Item label="消费次数">{detail.total_orders}次</Descriptions.Item>
              <Descriptions.Item label="累计消费">{formatMoney(detail.total_amount)}</Descriptions.Item>
              <Descriptions.Item label="平均客单">{formatMoney(detail.average_order_amount)}</Descriptions.Item>
              <Descriptions.Item label="最近消费">{detail.sleep_days}天前</Descriptions.Item>
            </Descriptions>
            <h4 style={{ marginTop: 24 }}>消费记录</h4>
            <Table
              rowKey="id"
              size="small"
              pagination={false}
              dataSource={detail.orders}
              columns={[
                { title: "日期", dataIndex: "order_date" },
                { title: "类型", dataIndex: "order_type" },
                { title: "人数", dataIndex: "people_count" },
                { title: "金额", dataIndex: "amount", render: (value) => formatMoney(value) },
              ]}
            />
          </>
        ) : null}
      </Drawer>
    </div>
  );
}
