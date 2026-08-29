import { Button, Card, Descriptions, Tag } from "antd";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchSettings, logout } from "../../api/auth";
import type { AppSettings } from "../../types";

export default function Settings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<AppSettings | null>(null);

  useEffect(() => {
    fetchSettings().then(setSettings).catch(() => undefined);
  }, []);

  return (
    <Card title="系统设置">
      <Descriptions column={1} bordered>
        <Descriptions.Item label="门店">{settings?.store_name || "青岛城阳宴江南（汇海路店）"}</Descriptions.Item>
        <Descriptions.Item label="登录账号">{settings?.username || "admin"}</Descriptions.Item>
        <Descriptions.Item label="演示模式">
          {settings?.demo_mode ? <Tag color="gold">已开启 DEMO_MODE</Tag> : <Tag color="green">真实 AI 已配置</Tag>}
        </Descriptions.Item>
        <Descriptions.Item label="说明">
          当前为演示型 MVP，使用模拟经营数据。正式合作后可对接门店真实会员、收银或客户管理系统。
        </Descriptions.Item>
      </Descriptions>
      <Button
        danger
        style={{ marginTop: 24 }}
        onClick={() => {
          logout();
          navigate("/login");
        }}
      >
        退出登录
      </Button>
    </Card>
  );
}
