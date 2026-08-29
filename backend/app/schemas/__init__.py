from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    customer_name: str
    phone: str
    gender: str
    age: int | None = None
    customer_level: str
    total_orders: int
    total_amount: float
    last_order_date: date | None = None
    average_order_amount: float
    birthday: date | None = None
    tags: str


class CustomerListItem(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sleep_days: int = 0
    tag_list: list[str] = Field(default_factory=list)


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    order_date: date
    amount: float
    people_count: int
    order_type: str
    table_type: str


class CustomerDetail(CustomerListItem):
    orders: list[OrderItem] = Field(default_factory=list)
    order_types: list[str] = Field(default_factory=list)


class CustomerListResponse(BaseModel):
    total: int
    items: list[CustomerListItem]


class DashboardOverview(BaseModel):
    today_revenue: float
    today_orders: int
    average_order_amount: float
    customer_count: int
    old_customer_rate: float
    pending_followups: int
    high_value_sleeping_count: int
    banquet_pending_count: int
    forecast_revenue: float = 0
    revenue_change: float = 0
    order_change: float = 0
    aov_change: float = 0
    week_change: float = 0
    score: int = 0
    stars_label: str = ""
    recommendation: str = ""
    diagnosis: list[dict] = Field(default_factory=list)
    menu_counts: dict[str, int] = Field(default_factory=dict)


class DashboardInsight(BaseModel):
    level: str
    title: str
    suggestion: str


class DashboardTrendPoint(BaseModel):
    date: str
    revenue: float
    orders: int


class DashboardOverviewResponse(DashboardOverview):
    insights: list[DashboardInsight]
    trend: list[DashboardTrendPoint]
    level_distribution: dict[str, int]


class RecallCustomerItem(CustomerListItem):
    recall_priority: int
    recall_priority_label: str


class RecallListResponse(BaseModel):
    total: int
    high_value_sleeping_count: int
    items: list[RecallCustomerItem]


class RecallAnalyzeResult(BaseModel):
    customer_value: str
    customer_value_score: int
    customer_status: str
    churn_risk: str
    judgment: str
    recall_suggestion: str
    recommended_channel: str
    recommended_offer: str
    demo_fallback: bool = False


class RecallMessageResult(BaseModel):
    message: str
    demo_fallback: bool = False


class MarketingGenerateRequest(BaseModel):
    goal: str
    dish: str
    promotion: str
    target_customer: str = ""
    date_range: str = ""


class MarketingPlan(BaseModel):
    theme: str
    target_customer: str
    strategy: str
    activity_suggestion: str
    moments_copy: str
    wechat_group_copy: str
    staff_script: str
    dianping_copy: str
    demo_fallback: bool = False


class ReviewItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    rating: int
    content: str
    review_date: date
    source: str
    tags: str
    sentiment: str


class ReviewListResponse(BaseModel):
    total: int
    average_rating: float
    positive_rate: float
    negative_rate: float
    items: list[ReviewItem]


class ReviewSuggestion(BaseModel):
    finding: str
    suggestion: str


class ReviewAnalyzeResult(BaseModel):
    likes: list[str]
    complaints: list[str]
    focus: list[str]
    hot_dishes: list[str]
    hot_scenes: list[str]
    service_issues: list[str]
    suggestions: list[ReviewSuggestion]
    demo_fallback: bool = False


class BanquetLeadItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    phone: str
    event_type: str
    people_count: int
    expected_amount: str
    event_date: date | None = None
    source: str
    status: str
    notes: str


class BanquetLeadCreate(BaseModel):
    customer_name: str
    phone: str
    event_type: str
    people_count: int
    expected_amount: str
    event_date: date | None = None
    source: str
    status: str = "待跟进"
    notes: str = ""


class BanquetLeadUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class BanquetLeadListResponse(BaseModel):
    total: int
    items: list[BanquetLeadItem]


class BanquetAnalyzeResult(BaseModel):
    customer_value: str
    customer_value_score: int
    deal_potential: str
    reason: str
    followup_suggestion: str
    next_step: str
    script: str
    demo_fallback: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    store_name: str


class SettingsResponse(BaseModel):
    store_name: str
    demo_mode: bool
    ai_configured: bool
    username: str
