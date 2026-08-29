import {
  BulbOutlined,
  FileTextOutlined,
  GiftOutlined,
  LogoutOutlined,
  SettingOutlined,
  ShopOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  UserSwitchOutlined,
} from "@ant-design/icons";
import { Layout, Menu } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { logout } from "../api/auth";

const { Sider, Header, Content } = Layout;

const items = [
  { key: "/dashboard", icon: <ShopOutlined />, label: "AI经营驾驶舱" },
  { key: "/opportunities", icon: <BulbOutlined />, label: "AI经营机会中心" },
  { key: "/ai-daily-report", icon: <FileTextOutlined />, label: "AI老板日报" },
  {
    key: "ops",
    icon: <ThunderboltOutlined />,
    label: "经营分析",
    children: [
      { key: "/revenue-analysis", label: "营业额分析" },
      { key: "/menu-analysis", label: "菜品经营分析" },
      { key: "/menu-diagnosis", label: "菜单诊断" },
      { key: "/table-efficiency", label: "翻台效率分析" },
    ],
  },
  { key: "/staff-assistant", icon: <TeamOutlined />, label: "AI员工助手" },
  {
    key: "crm",
    icon: <UserSwitchOutlined />,
    label: "客户经营",
    children: [
      { key: "/customers", label: "客户管理" },
      { key: "/customer-recall", label: "AI客户召回" },
      { key: "/banquet-leads", label: "宴请客户" },
    ],
  },
  {
    key: "mkt",
    icon: <GiftOutlined />,
    label: "AI营销",
    children: [
      { key: "/marketing", label: "AI营销助手" },
      { key: "/reviews", label: "AI评价分析" },
    ],
  },
  { key: "/settings", icon: <SettingOutlined />, label: "系统设置" },
];

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const store = localStorage.getItem("yjn_store") || "青岛城阳宴江南（汇海路店）";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={232} style={{ background: "#1f2933" }}>
        <div className="sidebar-logo">
          <div>
            宴江南
            <span className="sub">AI老板经营诊断</span>
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={["ops", "crm", "mkt"]}
          items={items}
          onClick={(event) => {
            if (event.key.startsWith("/")) {
              navigate(event.key);
            }
          }}
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
