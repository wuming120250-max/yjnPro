import { type ReactNode, Suspense, lazy } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import { isLoggedIn } from "../api/auth";
import MainLayout from "../layouts/MainLayout";
import Login from "../pages/Login";

const Dashboard = lazy(() => import("../pages/Dashboard"));
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
      {
        path: "dashboard",
        element: (
          <Suspense fallback={<PageFallback />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: "customers",
        element: (
          <Suspense fallback={<PageFallback />}>
            <Customers />
          </Suspense>
        ),
      },
      {
        path: "customer-recall",
        element: (
          <Suspense fallback={<PageFallback />}>
            <CustomerRecall />
          </Suspense>
        ),
      },
      {
        path: "marketing",
        element: (
          <Suspense fallback={<PageFallback />}>
            <Marketing />
          </Suspense>
        ),
      },
      {
        path: "reviews",
        element: (
          <Suspense fallback={<PageFallback />}>
            <Reviews />
          </Suspense>
        ),
      },
      {
        path: "banquet-leads",
        element: (
          <Suspense fallback={<PageFallback />}>
            <BanquetLeads />
          </Suspense>
        ),
      },
      {
        path: "settings",
        element: (
          <Suspense fallback={<PageFallback />}>
            <Settings />
          </Suspense>
        ),
      },
    ],
  },
]);
