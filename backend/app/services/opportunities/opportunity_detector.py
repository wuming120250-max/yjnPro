from __future__ import annotations

import re
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.banquet_lead import BanquetLead
from app.models.customer import Customer
from app.models.daily_revenue import DailyRevenue
from app.models.review import Review
from app.services.customer_service import current_biz_date, sleep_days
from app.services.menu_service import POTENTIAL, STAR, classify_menu
from app.services.recall_service import list_recall_customers
from app.services.table_service import peak_slot_summary

SERVICE_KEYWORDS = ("上菜慢", "上菜速度", "等菜", "等了很久", "服务慢", "有点慢", "等了挺久")


def _pct(current: float, previous: float) -> float:
    if not previous:
        return 0
    return round((current - previous) / previous * 100, 1)


def _amount_high(text: str) -> int:
    nums = [int(item) for item in re.findall(r"\d+", text or "")]
    return max(nums) if nums else 0


def _candidate(**kwargs) -> dict:
    kwargs.setdefault("action_items", [])
    return kwargs


def detect_opportunities(db: Session) -> list[dict]:
    today = current_biz_date()
    stamp = today.strftime("%Y%m%d")
    found: list[dict] = []
    found.extend(_detect_revenue(db, today, stamp))
    found.extend(_detect_menu(db, stamp))
    found.extend(_detect_customers(db, today, stamp))
    found.extend(_detect_service(db, today, stamp))
    found.extend(_detect_banquet(db, stamp))
    return found[:8]


def _detect_revenue(db: Session, today, stamp: str) -> list[dict]:
    rows = list(db.scalars(select(DailyRevenue).order_by(DailyRevenue.date.asc())).all())
    if not rows:
        return []
    window = [row for row in rows if row.date >= today - timedelta(days=6)]
    if len(window) < 3:
        window = rows[-7:]
    avg_revenue = sum(float(row.revenue) for row in window) / len(window)
    avg_orders = sum(row.order_count for row in window) / len(window)
    avg_aov = sum(float(row.average_order_amount) for row in window) / len(window)
    avg_family = sum(row.family_orders for row in window) / len(window)
    today_row = next((row for row in window if row.date == today), window[-1])
    worst = min(window, key=lambda row: float(row.revenue))
    recent7 = [row for row in rows if today - timedelta(days=6) <= row.date <= today]
    prev7 = [row for row in rows if today - timedelta(days=13) <= row.date <= today - timedelta(days=7)]
    recent_family = sum(row.family_orders for row in recent7)
    prev_family = sum(row.family_orders for row in prev7) or 0
    items: list[dict] = []

    if float(today_row.revenue) < avg_revenue * 0.90 or float(worst.revenue) < avg_revenue * 0.90:
        target = today_row if float(today_row.revenue) < avg_revenue * 0.90 else worst
        drop = abs(_pct(float(target.revenue), avg_revenue))
        impact = round(avg_revenue - float(target.revenue), 0)
        items.append(
            _candidate(
                opportunity_key=f"revenue_decline_{target.date.strftime('%Y%m%d')}",
                title="营业额异常下降",
                type="revenue",
                description=(
                    f"{target.date.isoformat()} 营业额 ¥{float(target.revenue):.0f}，"
                    f"较近7日平均 ¥{avg_revenue:.0f} 下降 {drop}%。"
                ),
                data_source="daily_revenue",
                data_snapshot={
                    "date": target.date.isoformat(),
                    "current_revenue": float(target.revenue),
                    "average_revenue": round(avg_revenue, 0),
                    "decline_rate": drop,
                    "dinner_revenue": float(target.dinner_revenue),
                    "family_orders": target.family_orders,
                    "note": "模拟估算",
                },
                reason="晚餐客流下降更明显，客单价变化不大，不是消费能力突然变差。",
                estimated_impact=max(impact, 3000),
                impact_type="revenue",
                suggestion="重点看晚餐客流和家庭聚餐，而不是单纯降价。",
                action="打开营业异常分析，核对晚餐和家庭聚餐订单",
                summary="近期出现明显营业额下滑，主要来自晚餐客流，建议先查家庭聚餐场景。",
                link="/revenue-analysis",
                score_inputs={"impact": 30, "urgency": 18, "frequency": 15, "executability": 11},
                action_items=["核对晚餐订单下降幅度", "查看4～6人聚餐是否同步下滑", "准备家庭聚餐套餐方案"],
            )
        )

    family_drop = False
    if prev_family and recent_family < prev_family * 0.90:
        family_drop = True
        current_val, previous_val = recent_family, prev_family
        desc = f"近7天家庭聚餐相关订单 {recent_family} 桌，上一周 {prev_family} 桌，下降 {abs(_pct(recent_family, prev_family))}%。"
    elif avg_family and worst.family_orders < avg_family * 0.85:
        family_drop = True
        current_val, previous_val = worst.family_orders, round(avg_family)
        desc = (
            f"{worst.date.isoformat()} 家庭聚餐订单 {worst.family_orders} 桌，"
            f"近7日平均约 {avg_family:.0f} 桌，下降 {abs(_pct(worst.family_orders, avg_family))}%。"
        )
    if family_drop:
        items.append(
            _candidate(
                opportunity_key=f"revenue_family_dining_{stamp}",
                title="家庭聚餐订单下降，可推套餐",
                type="revenue",
                description=desc,
                data_source="daily_revenue",
                data_snapshot={
                    "current": current_val,
                    "previous": previous_val,
                    "decline_rate": abs(_pct(float(current_val), float(previous_val))),
                    "weekly_opportunity": 3120,
                    "note": "模拟估算",
                },
                reason="4～6人聚餐下滑，适合用家庭套餐把客群拉回来。",
                estimated_impact=3120,
                impact_type="revenue",
                suggestion="针对家庭聚餐客户推出 4 人套餐，并让服务员重点推荐高毛利菜。",
                action="创建家庭聚餐套餐并让服务员开口推荐",
                summary="家庭聚餐订单最近偏弱，预计每周约有三千元量级营业机会，建议今天就推 4 人套餐。",
                link="/marketing",
                score_inputs={"impact": 30, "urgency": 18, "frequency": 15, "executability": 15},
                action_items=["设计 4～6 人家庭聚餐套餐", "把潜力菜写入服务员推荐话术", "针对周末家庭客群做一次触达"],
            )
        )

    if today_row.order_count < avg_orders * 0.85:
        items.append(
            _candidate(
                opportunity_key=f"revenue_orders_{stamp}",
                title="订单量异常下降",
                type="revenue",
                description=f"今日订单 {today_row.order_count} 单，低于近7日平均 {avg_orders:.0f} 单。",
                data_source="daily_revenue",
                data_snapshot={
                    "today_orders": today_row.order_count,
                    "avg_orders": round(avg_orders, 1),
                },
                reason="订单下降通常是客流问题，需要结合晚餐时段看。",
                estimated_impact=2000,
                impact_type="revenue",
                suggestion="先看晚餐高峰到店量，再决定要不要做引流。",
                action="核对今日晚餐订单和翻台",
                summary="今日订单低于近7日平均，建议先确认是不是晚餐客流变少。",
                link="/revenue-analysis",
                score_inputs={"impact": 20, "urgency": 15, "frequency": 8, "executability": 10},
            )
        )

    if float(today_row.average_order_amount) < avg_aov * 0.90:
        items.append(
            _candidate(
                opportunity_key=f"revenue_aov_{stamp}",
                title="客单价下降",
                type="revenue",
                description=(
                    f"今日客单价 ¥{float(today_row.average_order_amount):.0f}，"
                    f"低于近7日平均 ¥{avg_aov:.0f}。"
                ),
                data_source="daily_revenue",
                data_snapshot={
                    "today_aov": float(today_row.average_order_amount),
                    "avg_aov": round(avg_aov, 2),
                },
                reason="客单价下降时，更适合推高毛利菜，而不是继续打低价。",
                estimated_impact=1500,
                impact_type="revenue",
                suggestion="让服务员主推明星菜和潜力菜。",
                action="打开员工助手，按家庭聚餐做一版推荐",
                summary="客单价偏低，可以通过推荐高毛利菜把利润补回来。",
                link="/staff-assistant",
                score_inputs={"impact": 20, "urgency": 8, "frequency": 8, "executability": 15},
            )
        )
    return items


def _detect_menu(db: Session, stamp: str) -> list[dict]:
    menu = classify_menu(db)
    items: list[dict] = []
    stars = [row for row in menu["items"] if row["quadrant"] == STAR]
    pots = [row for row in menu["items"] if row["quadrant"] == POTENTIAL]
    star = next((row for row in stars if row["name"] == "烤腱子肉"), stars[0] if stars else None)
    pot = next((row for row in pots if "芋头" in row["name"]), pots[0] if pots else None)
    if star:
        items.append(
            _candidate(
                opportunity_key=f"menu_star_{star['id']}_{stamp}",
                title=f"{star['name']}是高价值明星菜",
                type="menu",
                description=(
                    f"{star['name']}销量 {star['sales_count']} 份，毛利率 {star['gross_margin']}%，"
                    f"趋势 {star['sales_trend']:+.0f}%。"
                ),
                data_source="menu_items",
                data_snapshot={
                    "name": star["name"],
                    "sales_count": star["sales_count"],
                    "gross_margin": star["gross_margin"],
                    "sales_trend": star["sales_trend"],
                    "price": star["price"],
                    "cost_price": star["cost_price"],
                    "note": "菜品成本为模拟数据",
                },
                reason="卖得多同时利润也好，值得继续作为招牌主推。",
                estimated_impact=1800,
                impact_type="revenue",
                suggestion="继续作为重点推荐菜，并放到家庭套餐里。",
                action="把该菜加入今日服务员推荐",
                summary=f"{star['name']}销量高、毛利高，是当前最值得继续主推的菜。",
                link="/menu-analysis",
                score_inputs={"impact": 20, "urgency": 8, "frequency": 8, "executability": 15},
                action_items=["保持该菜高峰期备货", "写入服务员推荐话术"],
            )
        )
    if pot:
        items.append(
            _candidate(
                opportunity_key=f"menu_potential_{pot['id']}_{stamp}",
                title=f"{pot['name']}是高毛利潜力菜",
                type="menu",
                description=(
                    f"{pot['name']}毛利率 {pot['gross_margin']}%，但销量只有 {pot['sales_count']} 份，低于平均。"
                ),
                data_source="menu_items",
                data_snapshot={
                    "name": pot["name"],
                    "sales_count": pot["sales_count"],
                    "gross_margin": pot["gross_margin"],
                    "avg_sales": menu["avg_sales"],
                    "avg_margin": menu["avg_margin"],
                    "note": "菜品成本为模拟数据",
                },
                reason="利润好但曝光不够，服务员主动推荐就能把销量拉起来。",
                estimated_impact=2400,
                impact_type="revenue",
                suggestion="让服务员重点推荐，不要只推已经卖得很好的菜。",
                action="把高毛利潜力菜加入服务员推荐菜单",
                summary=f"{pot['name']}毛利高但销量偏低，是最容易通过推荐转化的增长机会。",
                link="/menu-analysis",
                score_inputs={"impact": 25, "urgency": 8, "frequency": 20, "executability": 15},
                action_items=["加入员工推荐菜话术", "评估是否进入家庭套餐"],
            )
        )
    return items


def _detect_customers(db: Session, today, stamp: str) -> list[dict]:
    customers = list(db.scalars(select(Customer)).all())
    if not customers:
        return []
    avg_spend = sum(float(row.total_amount) for row in customers) / len(customers)
    sleeping = [
        row
        for row in customers
        if float(row.total_amount) > avg_spend * 2 and sleep_days(row.last_order_date, today) >= 60
    ]
    if not sleeping:
        sleeping = [
            row
            for row in customers
            if float(row.total_amount) >= 3000 and sleep_days(row.last_order_date, today) >= 60
        ]
    if len(sleeping) < 8:
        seen = {row.id for row in sleeping}
        for row in list_recall_customers(db):
            if row.id not in seen:
                sleeping.append(row)
            if len(sleeping) >= 12:
                break
    if len(sleeping) < 3:
        return []
    sleeping.sort(key=lambda row: float(row.total_amount), reverse=True)
    names = [row.customer_name for row in sleeping[:8]]
    return [
        _candidate(
            opportunity_key=f"customer_high_value_sleeping_{stamp}",
            title=f"{len(sleeping)}名高价值客户待召回",
            type="customer",
            description=(
                f"有 {len(sleeping)} 名客户累计消费明显高于平均水平，且超过 60 天未到店。"
                f"例如：{'、'.join(names[:5])}。"
            ),
            data_source="customers",
            data_snapshot={
                "count": len(sleeping),
                "avg_spend": round(avg_spend, 0),
                "examples": names[:8],
                "threshold_days": 60,
            },
            reason="这些客户曾经贡献过较多营业额，召回成本低于重新获客。",
            estimated_impact=round(sum(float(row.average_order_amount) for row in sleeping[:8]), 0),
            impact_type="customer",
            suggestion="优先用微信做个性化召回，而不是群发同样优惠。",
            action="打开客户召回，先处理名单前 8 人",
            summary=f"有 {len(sleeping)} 名高价值客户超过 60 天未消费，今天最值得先召回，而不是对所有人做一样的营销。",
            link="/customer-recall",
            score_inputs={"impact": 25, "urgency": 18, "frequency": 15, "executability": 10},
            action_items=["筛选高价值沉睡客户", "生成召回话术", "安排店长跟进"],
        )
    ]


def _detect_service(db: Session, today, stamp: str) -> list[dict]:
    items: list[dict] = []
    peak = peak_slot_summary(db, today)
    if peak.get("is_abnormal"):
        extra = round((peak["avg_duration"] - peak["normal_duration"]) / peak["normal_duration"] * 100)
        items.append(
            _candidate(
                opportunity_key=f"service_peak_efficiency_{stamp}",
                title="晚餐高峰效率下降",
                type="service",
                description=(
                    f"{peak['label']} 平均用餐 {peak['avg_duration']} 分钟，"
                    f"正常 {peak['normal_duration']} 分钟，偏慢约 {extra}%。"
                ),
                data_source="table_orders",
                data_snapshot={
                    "label": peak["label"],
                    "avg_duration": peak["avg_duration"],
                    "normal_duration": peak["normal_duration"],
                    "table_count": peak["table_count"],
                    "utilization": peak.get("utilization"),
                    "note": "翻台数据为 Demo 模拟数据",
                },
                reason="高峰期出餐和结账变慢，会直接卡住桌台周转和晚餐营业额。",
                estimated_impact=3200,
                impact_type="efficiency",
                suggestion="重点检查该时段热门菜出餐、加菜和结账等待。",
                action="检查 18:30～19:30 出餐流程",
                summary="晚餐高峰用餐时间明显变长，可能影响翻台。建议今天先查该时段出餐和结账。",
                link="/table-efficiency",
                score_inputs={"impact": 40, "urgency": 25, "frequency": 15, "executability": 6},
                action_items=["检查 18:30～19:30 出餐流程", "查看热门菜出餐时间", "与前厅负责人确认高峰期问题"],
            )
        )

    since = today - timedelta(days=29)
    reviews = list(db.scalars(select(Review).where(Review.review_date >= since)).all())
    matched = []
    weekend = 0
    for row in reviews:
        blob = f"{row.content} {row.tags}"
        if any(key in blob for key in SERVICE_KEYWORDS):
            matched.append(row)
            if row.review_date.weekday() >= 4:
                weekend += 1
    if len(matched) >= 3:
        items.append(
            _candidate(
                opportunity_key=f"service_slow_reviews_{stamp}",
                title="周末上菜速度评价变多",
                type="service",
                description=(
                    f"最近 30 天有 {len(matched)} 条评价提到上菜慢或等待，"
                    f"其中周五/周六/周日 {weekend} 条。"
                ),
                data_source="reviews",
                data_snapshot={
                    "count": len(matched),
                    "weekend_count": weekend,
                    "samples": [row.content for row in matched[:5]],
                },
                reason="评价里的上菜慢，和高峰翻台变慢是同一类问题，值得老板亲自看一眼。",
                estimated_impact=2000,
                impact_type="efficiency",
                suggestion="把评价问题和高峰翻台放在一起看，优先改周末晚餐出餐。",
                action="打开评价分析，核对上菜速度投诉",
                summary="上菜慢相关评价在周末更集中，说明高峰期服务效率已经开始影响口碑。",
                link="/reviews",
                score_inputs={"impact": 20, "urgency": 18, "frequency": 15, "executability": 10},
                action_items=["查看近 30 天上菜速度评价", "对照高峰翻台数据", "安排周末值班加强出餐"],
            )
        )
    return items


def _detect_banquet(db: Session, stamp: str) -> list[dict]:
    leads = list(
        db.scalars(select(BanquetLead).where(BanquetLead.status == "待跟进")).all()
    )
    high = [
        row
        for row in leads
        if _amount_high(row.expected_amount) >= 5000
        or "公司" in (row.event_type or "")
        or "商务" in (row.event_type or "")
    ]
    high = [row for row in high if _amount_high(row.expected_amount) >= 5000] or high[:3]
    if len(high) < 1:
        return []
    names = [f"{row.customer_name}（{row.event_type}/{row.expected_amount}）" for row in high[:5]]
    return [
        _candidate(
            opportunity_key=f"banquet_high_value_{stamp}",
            title=f"{len(high)}个高价值宴请客户待跟进",
            type="banquet",
            description="、".join(names) + "，预算较高但仍是待跟进。",
            data_source="banquet_leads",
            data_snapshot={
                "count": len(high),
                "examples": names,
            },
            reason="高预算宴请成交一单，往往超过普通散客很多天的利润。",
            estimated_impact=5000,
            impact_type="revenue",
            suggestion="今天先联系预算明确、日期临近的客户，确认菜单和包间。",
            action="打开宴请客户，跟进高预算待跟进名单",
            summary=f"有 {len(high)} 个高预算宴请还在待跟进，今天打几个电话就可能锁定一单。",
            link="/banquet-leads",
            score_inputs={"impact": 30, "urgency": 15, "frequency": 8, "executability": 15},
            action_items=["筛选预算 5000 以上待跟进客户", "准备包间和菜单方案", "当天完成至少 1 次跟进"],
        )
    ]
