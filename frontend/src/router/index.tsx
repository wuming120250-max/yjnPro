import { type ReactNode, Suspense, lazy } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import { isLoggedIn } from "../api/auth";
import MainLayout from "../layouts/MainLayout";
import Login from "../pages/Login";

const Dashboard = lazy(() => import("../pages/Dashboard"));
const Opportunities = lazy(() => import("../pages/Opportunities"));
const AIDailyReport = lazy(() => import("../pages/AIDailyReport"));
const MenuAnalysis = lazy(() => import("../pages/MenuAnalysis"));
const MenuDiagnosis = lazy(() => import("../pages/MenuDiagnosis"));
const RevenueAnalysis = lazy(() => import("../pages/RevenueAnalysis"));
const TableEfficiency = lazy(() => import("../pages/TableEfficiency"));
const StaffAssistant = lazy(() => import("../pages/StaffAssistant"));
const Customers = lazy(() => import("../pages/Customers"));
const CustomerRecall = lazy(() => import("../pages/CustomerRecall"));
const Marketing = lazy(() => import("../pages/Marketing"));
const Reviews = lazy(() => import("../pages/Reviews"));
const BanquetLeads = lazy(() => import("../pages/BanquetLeads"));
const Settings = lazy(() => import("../pages/Settings"));

function Guard({ children }: { children: ReactNode }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function PageFallback() {
  return <div style={{ padding: 32 }}>页面加载中…</div>;
}

function wrap(element: ReactNode) {
  return <Suspense fallback={<PageFallback />}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: (
      <Guard>
        <MainLayout />
      </Guard>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: wrap(<Dashboard />) },
      { path: "opportunities", element: wrap(<Opportunities />) },
      { path: "ai-daily-report", element: wrap(<AIDailyReport />) },
      { path: "menu-analysis", element: wrap(<MenuAnalysis />) },
      { path: "menu-diagnosis", element: wrap(<MenuDiagnosis />) },
      { path: "revenue-analysis", element: wrap(<RevenueAnalysis />) },
      { path: "table-efficiency", element: wrap(<TableEfficiency />) },
      { path: "staff-assistant", element: wrap(<StaffAssistant />) },
      { path: "customers", element: wrap(<Customers />) },
      { path: "customer-recall", element: wrap(<CustomerRecall />) },
      { path: "marketing", element: wrap(<Marketing />) },
      { path: "reviews", element: wrap(<Reviews />) },
      { path: "banquet-leads", element: wrap(<BanquetLeads />) },
      { path: "settings", element: wrap(<Settings />) },
    ],
  },
]);
