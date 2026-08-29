import { Button, Form, Input, Typography, message } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../../api/auth";
import { getErrorMessage } from "../../api/client";

export default function Login() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  return (
    <div className="login-page">
      <div className="login-brand">
        <div style={{ letterSpacing: "0.24em", fontSize: 13, opacity: 0.7 }}>QINGDAO CHENGYANG</div>
        <h1>宴江南</h1>
        <p>
          AI 门店经营助手。不是再做一套收银或点餐系统，而是帮老板把客户、消费和评价数据用起来：发现该召回谁、该怎么说、哪些宴请值得跟进。
        </p>
      </div>
      <div className="login-form-wrap">
        <div className="login-card">
          <Typography.Title level={4} style={{ marginTop: 0 }}>
            管理员登录
          </Typography.Title>
          <Typography.Paragraph type="secondary">青岛城阳宴江南（汇海路店）演示环境</Typography.Paragraph>
          <Form
            layout="vertical"
            initialValues={{ username: "admin", password: "admin123" }}
            onFinish={async (values) => {
              setLoading(true);
              try {
                await login(values.username, values.password);
                navigate("/dashboard");
              } catch (error) {
                message.error(getErrorMessage(error, "登录失败"));
              } finally {
                setLoading(false);
              }
            }}
          >
            <Form.Item name="username" label="账号" rules={[{ required: true }]}>
              <Input placeholder="admin" />
            </Form.Item>
            <Form.Item name="password" label="密码" rules={[{ required: true }]}>
              <Input.Password placeholder="admin123" />
            </Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading} size="large">
              进入系统
            </Button>
          </Form>
        </div>
      </div>
    </div>
  );
}
