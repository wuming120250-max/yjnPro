import {
  CommentOutlined,
  CrownOutlined,
  GiftOutlined,
  LogoutOutlined,
  SettingOutlined,
  ShopOutlined,
  TeamOutlined,
  UserSwitchOutlined,
} from "@ant-design/icons";
import { Layout, Menu } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { logout } from "../api/auth";

const { Sider, Header, Content } = Layout;

const items = [
  { key: "/dashboard", icon: <ShopOutlined />, label: "AI经营驾驶舱" },
  { key: "/customers", icon: <TeamOutlined />, label: "客户管理" },
  { key: "/customer-recall", icon: <UserSwitchOutlined />, label: "AI客户召回" },
  { key: "/marketing", icon: <GiftOutlined />, label: "AI营销助手" },
  { key: "/reviews", icon: <CommentOutlined />, label: "AI评价分析" },
  { key: "/banquet-leads", icon: <CrownOutlined />, label: "宴请客户" },
  { key: "/settings", icon: <SettingOutlined />, label: "系统设置" },
];

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const store = localStorage.getItem("yjn_store") || "青岛城阳宴江南（汇海路店）";
  const selected = items.find((item) => location.pathname.startsWith(item.key))?.key || "/dashboard";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={232} style={{ background: "#1f2933" }}>
        <div className="sidebar-logo">
          <div>
            宴江南
            <span className="sub">AI 门店经营助手</span>
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selected]}
          items={items}
          onClick={(event) => navigate(event.key)}
          style={{ background: "#1f2933", borderInlineEnd: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid #eee6dc",
          }}
        >
          <div style={{ fontWeight: 600 }}>{store}</div>
          <a
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            <LogoutOutlined /> 退出
          </a>
        </Header>
        <Content>
          <div className="page-shell">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
