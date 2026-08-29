export interface LoginResponse {
  token: string;
  username: string;
  store_name: string;
}

export interface AppSettings {
  store_name: string;
  demo_mode: boolean;
  ai_configured: boolean;
  username: string;
}

export interface DashboardInsight {
  level: string;
  title: string;
  suggestion: string;
}

export interface DashboardTrendPoint {
  date: string;
  revenue: number;
  orders: number;
}

export interface DashboardOverview {
  today_revenue: number;
  today_orders: number;
  average_order_amount: number;
  customer_count: number;
  old_customer_rate: number;
  pending_followups: number;
  high_value_sleeping_count: number;
  banquet_pending_count: number;
  forecast_revenue: number;
  revenue_change: number;
  order_change: number;
  aov_change: number;
  week_change: number;
  score: number;
  stars_label: string;
  recommendation: string;
  diagnosis: DiagnosisItem[];
  menu_counts: Record<string, number>;
  insights: DashboardInsight[];
  trend: DashboardTrendPoint[];
  level_distribution: Record<string, number>;
  top_opportunities: OpportunityItem[];
}

export interface DiagnosisItem {
  level: string;
  title: string;
  detail: string;
  reason: string;
  suggestion: string;
  link: string;
}

export interface CustomerItem {
  id: number;
  customer_name: string;
  phone: string;
  gender: string;
  age: number | null;
  customer_level: string;
  total_orders: number;
  total_amount: number;
  last_order_date: string | null;
  average_order_amount: number;
  birthday: string | null;
  tags: string;
  tag_list: string[];
  sleep_days: number;
}

export interface OrderItem {
  id: number;
  order_no: string;
  order_date: string;
  amount: number;
  people_count: number;
  order_type: string;
  table_type: string;
}

export interface CustomerDetail extends CustomerItem {
  orders: OrderItem[];
  order_types: string[];
}

export interface CustomerListResponse {
  total: number;
  items: CustomerItem[];
}

export interface RecallCustomerItem extends CustomerItem {
  recall_priority: number;
  recall_priority_label: string;
}

export interface RecallListResponse {
  total: number;
  high_value_sleeping_count: number;
  items: RecallCustomerItem[];
}

export interface RecallAnalyzeResult {
  customer_value: string;
  customer_value_score: number;
  customer_status: string;
  churn_risk: string;
  judgment: string;
  recall_suggestion: string;
  recommended_channel: string;
  recommended_offer: string;
  demo_fallback: boolean;
}

export interface RecallMessageResult {
  message: string;
  demo_fallback: boolean;
}

export interface MarketingPlan {
  theme: string;
  target_customer: string;
  strategy: string;
  activity_suggestion: string;
  moments_copy: string;
  wechat_group_copy: string;
  staff_script: string;
  dianping_copy: string;
  demo_fallback: boolean;
}

export interface ReviewItem {
  id: number;
  customer_name: string;
  rating: number;
  content: string;
  review_date: string;
  source: string;
  tags: string;
  sentiment: string;
}

export interface ReviewListResponse {
  total: number;
  average_rating: number;
  positive_rate: number;
  negative_rate: number;
  items: ReviewItem[];
}

export interface ReviewAnalyzeResult {
  likes: string[];
  complaints: string[];
  focus: string[];
  hot_dishes: string[];
  hot_scenes: string[];
  service_issues: string[];
  suggestions: { finding: string; suggestion: string }[];
  demo_fallback: boolean;
}

export interface BanquetLeadItem {
  id: number;
  customer_name: string;
  phone: string;
  event_type: string;
  people_count: number;
  expected_amount: string;
  event_date: string | null;
  source: string;
  status: string;
  notes: string;
}

export interface BanquetLeadListResponse {
  total: number;
  items: BanquetLeadItem[];
}

export interface BanquetAnalyzeResult {
  customer_value: string;
  customer_value_score: number;
  deal_potential: string;
  reason: string;
  followup_suggestion: string;
  next_step: string;
  script: string;
  demo_fallback: boolean;
}

export interface MenuDish {
  id: number;
  name: string;
  category: string;
  price: number;
  cost_price: number;
  gross_profit: number;
  gross_margin: number;
  sales_count: number;
  sales_amount: number;
  sales_trend: number;
  quadrant: string;
  advice: string;
}

export interface MenuAnalysis {
  avg_sales: number;
  avg_margin: number;
  items: MenuDish[];
  counts: Record<string, number>;
}

export interface DailyReport {
  report_date: string;
  score: number;
  stars_label: string;
  today_revenue: number;
  today_orders: number;
  average_order_amount: number;
  revenue_change: number;
  summary: string;
  warnings: string[];
  positives: string[];
  opportunities: string[];
  recommendation: string;
  diagnosis: DiagnosisItem[];
  demo_fallback: boolean;
}

export interface OpportunityItem {
  id: number;
  opportunity_key: string;
  title: string;
  type: string;
  type_label: string;
  priority: number;
  level: string;
  level_label: string;
  description: string;
  data_source: string;
  data_snapshot: Record<string, unknown>;
  reason: string;
  estimated_impact: number;
  impact_type: string;
  impact_type_label: string;
  suggestion: string;
  action: string;
  summary: string;
  link: string;
  status: string;
  status_label: string;
  is_today_focus: boolean;
  due_date: string | null;
  completed_at: string | null;
  action_items: string[];
  demo_note: string;
  demo_fallback?: boolean;
}

export interface OpportunityListResponse {
  total: number;
  items: OpportunityItem[];
  stats: {
    total: number;
    high: number;
    medium: number;
    low: number;
    completed: number;
    pending: number;
    processing: number;
  };
  today_priority: OpportunityItem | null;
  biz_date: string;
  demo_mode: boolean;
  generated?: number;
  demo_fallback?: boolean;
}
