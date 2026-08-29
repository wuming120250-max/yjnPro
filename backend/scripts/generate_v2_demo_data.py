from __future__ import annotations

import csv
import random
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_demo_data import demo_dir

TODAY = date(2026, 8, 29)
RANDOM = random.Random(20260829)
NORMAL_DURATION = 72
PEAK_DURATION = 96


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output = {}
            for key in fieldnames:
                value = row[key]
                if isinstance(value, (date, datetime, time)):
                    output[key] = value.isoformat()
                else:
                    output[key] = value
            writer.writerow(output)


def _item(
    name: str,
    category: str,
    price: float,
    cost: float,
    sales_count: int,
    trend: float,
) -> dict:
    profit = round(price - cost, 2)
    margin = round(profit / price * 100, 1) if price else 0
    return {
        "name": name,
        "category": category,
        "price": price,
        "cost_price": cost,
        "gross_profit": profit,
        "gross_margin": margin,
        "sales_count": sales_count,
        "sales_amount": round(price * sales_count, 2),
        "sales_trend": trend,
        "status": "active",
    }


def build_menu_items() -> list[dict]:
    items = [
        _item("烤腱子肉", "热菜", 50, 19, 328, 23),
        _item("凤梨虾球", "热菜", 68, 24, 246, 12),
        _item("清蒸鲈鱼", "海鲜", 88, 32, 198, 8),
        _item("蒜蓉粉丝扇贝", "海鲜", 56, 18, 186, 6),
        _item("红烧肉", "热菜", 58, 21, 172, 5),
        _item("碟鱼头", "海鲜", 88, 30, 164, 9),
        _item("砂锅荔浦芋头", "热菜", 48, 14, 46, 4),
        _item("红烧狮子头", "热菜", 58, 16, 52, 3),
        _item("葱油鲍鱼", "海鲜", 98, 28, 41, 7),
        _item("干煸四季豆", "热菜", 32, 9, 58, 2),
        _item("清炒时蔬", "热菜", 28, 8, 61, 1),
        _item("芹菜拌海米", "凉菜", 38, 11, 54, 5),
        _item("家常豆腐", "热菜", 28, 16, 310, 2),
        _item("酸辣土豆丝", "热菜", 22, 13, 286, 1),
        _item("凉拌黄瓜", "凉菜", 18, 10, 264, 0),
        _item("米饭", "主食", 3, 1.2, 890, 1),
        _item("酸梅汤", "酒水", 12, 7, 240, -2),
        _item("油焖冬笋", "热菜", 42, 29, 18, -11),
        _item("芙蓉虾仁", "热菜", 78, 54, 22, -8),
        _item("蟹粉豆腐", "热菜", 68, 48, 16, -14),
        _item("特色例汤", "汤羹", 28, 9, 142, 4),
        _item("西红柿蛋汤", "汤羹", 22, 8, 118, 1),
        _item("拍黄瓜", "凉菜", 16, 6, 96, 0),
        _item("口水鸡", "凉菜", 48, 22, 88, 3),
        _item("白切鸡", "热菜", 68, 26, 74, 2),
        _item("糖醋排骨", "热菜", 58, 24, 81, 3),
        _item("宫保鸡丁", "热菜", 46, 18, 93, 1),
        _item("鱼香茄子", "热菜", 36, 14, 77, 2),
        _item("手撕包菜", "热菜", 26, 8, 69, 1),
        _item("蒜蓉西兰花", "热菜", 32, 10, 63, 2),
        _item("清炒荷兰豆", "热菜", 36, 12, 44, 1),
        _item("香辣蟹", "海鲜", 128, 52, 67, 6),
        _item("白灼虾", "海鲜", 98, 46, 71, 4),
        _item("葱姜炒蟹", "海鲜", 138, 58, 39, 2),
        _item("清蒸黄花鱼", "海鲜", 108, 44, 48, 3),
        _item("椒盐皮皮虾", "海鲜", 88, 36, 57, 5),
        _item("海参捞饭", "海鲜", 168, 72, 33, 8),
        _item("佛跳墙", "热菜", 198, 86, 21, -3),
        _item("东坡肘子", "热菜", 88, 34, 49, 2),
        _item("梅菜扣肉", "热菜", 62, 24, 58, 1),
        _item("干锅牛蛙", "热菜", 78, 32, 64, 4),
        _item("铁板牛柳", "热菜", 72, 30, 61, 3),
        _item("京酱肉丝", "热菜", 46, 18, 70, 1),
        _item("蚂蚁上树", "热菜", 32, 12, 55, 0),
        _item("酸菜鱼", "热菜", 88, 36, 76, 4),
        _item("水煮牛肉", "热菜", 78, 34, 59, 2),
        _item("麻婆豆腐", "热菜", 28, 11, 102, 1),
        _item("干煸肥肠", "热菜", 68, 29, 43, -1),
        _item("凉拌木耳", "凉菜", 22, 8, 80, 0),
        _item("皮蛋豆腐", "凉菜", 26, 9, 84, 1),
        _item("卤水拼盘", "凉菜", 58, 24, 62, 2),
        _item("蒜泥白肉", "凉菜", 48, 20, 51, 1),
        _item("玉米排骨汤", "汤羹", 48, 18, 66, 3),
        _item("老鸭汤", "汤羹", 68, 26, 47, 2),
        _item("西湖牛肉羹", "汤羹", 38, 14, 53, 1),
        _item("南瓜小米粥", "主食", 12, 4, 73, 2),
        _item("葱油拌面", "主食", 18, 6, 91, 3),
        _item("扬州炒饭", "主食", 28, 10, 88, 2),
        _item("馒头", "主食", 2, 0.6, 210, 0),
        _item("青岛啤酒", "酒水", 8, 4.5, 176, 1),
        _item("可乐", "酒水", 6, 3, 154, 0),
        _item("茉莉花茶", "酒水", 18, 5, 49, 2),
        _item("白酒小瓶", "酒水", 38, 18, 42, -2),
        _item("时令水果盘", "凉菜", 48, 22, 37, 1),
        _item("拔丝地瓜", "热菜", 32, 12, 29, -4),
        _item("奶油南瓜", "热菜", 36, 22, 19, -9),
        _item("芝士焗土豆", "热菜", 42, 28, 17, -12),
    ]
    return items


def build_daily_revenue() -> list[dict]:
    rows = []
    start = TODAY - timedelta(days=29)
    story = {
        date(2026, 8, 24): (26800, 126, 9800, 14800, 2200, 48, 78, 22),
        date(2026, 8, 25): (27100, 129, 9900, 15100, 2100, 49, 80, 24),
        date(2026, 8, 26): (26400, 124, 9700, 14600, 2100, 47, 77, 21),
        date(2026, 8, 27): (21600, 98, 9200, 10900, 1500, 44, 54, 12),
        date(2026, 8, 28): (24700, 114, 9400, 13600, 1700, 45, 69, 16),
        date(2026, 8, 29): (26800, 126, 9600, 14800, 2400, 46, 80, 26),
    }
    for offset in range(30):
        day = start + timedelta(days=offset)
        if day in story:
            revenue, orders, lunch, dinner, banquet, lunch_orders, dinner_orders, family = story[day]
        else:
            weekday = day.weekday()
            base = 25200 if weekday < 5 else 26800
            revenue = int(base + RANDOM.randint(-900, 1100))
            orders = int(revenue / RANDOM.randint(205, 230))
            lunch = int(revenue * 0.36)
            dinner = int(revenue * 0.55)
            banquet = revenue - lunch - dinner
            lunch_orders = int(orders * 0.38)
            dinner_orders = orders - lunch_orders
            family = int(orders * (0.18 if weekday >= 5 else 0.12))
        aov = round(revenue / orders, 2) if orders else 0
        rows.append(
            {
                "date": day,
                "revenue": revenue,
                "order_count": orders,
                "average_order_amount": aov,
                "lunch_revenue": lunch,
                "dinner_revenue": dinner,
                "banquet_revenue": banquet,
                "lunch_orders": lunch_orders,
                "dinner_orders": dinner_orders,
                "family_orders": family,
            }
        )
    return rows


def build_table_orders() -> list[dict]:
    tables = (
        [("大厅" + str(i), 4) for i in range(1, 9)]
        + [("小包间" + x, 8) for x in "ABCD"]
        + [("大包间1", 12), ("大包间2", 16)]
    )
    slots = [
        (time(11, 10), time(12, 20), False),
        (time(12, 5), time(13, 15), False),
        (time(13, 0), time(14, 10), False),
        (time(17, 20), time(18, 25), False),
        (time(18, 20), time(20, 0), True),
        (time(19, 10), time(20, 25), False),
        (time(20, 5), time(21, 15), False),
    ]
    rows = []
    start = TODAY - timedelta(days=29)
    for offset in range(30):
        day = start + timedelta(days=offset)
        used = RANDOM.sample(tables, k=RANDOM.randint(10, 14))
        for table_name, seats in used:
            for start_t, end_t, peak in slots:
                if RANDOM.random() < (0.92 if peak else 0.55):
                    if peak:
                        duration = PEAK_DURATION + RANDOM.randint(-4, 6)
                    else:
                        duration = NORMAL_DURATION + RANDOM.randint(-8, 8)
                    start_dt = datetime.combine(day, start_t) + timedelta(minutes=RANDOM.randint(-8, 8))
                    end_dt = start_dt + timedelta(minutes=duration)
                    amount = round(seats * RANDOM.uniform(68, 128) + (180 if peak else 0), 2)
                    order_type = "家庭聚餐" if seats >= 8 and RANDOM.random() < 0.4 else "普通用餐"
                    rows.append(
                        {
                            "table_name": table_name,
                            "seats": seats,
                            "order_date": day,
                            "start_time": start_dt.time().replace(microsecond=0),
                            "end_time": end_dt.time().replace(microsecond=0),
                            "duration_minutes": duration,
                            "amount": amount,
                            "order_type": order_type,
                        }
                    )
    return rows


def generate_v2(output_dir: Path | None = None) -> dict[str, int]:
    target = output_dir or demo_dir()
    menu_items = build_menu_items()
    daily_revenue = build_daily_revenue()
    table_orders = build_table_orders()
    _write_csv(
        target / "menu_items.csv",
        menu_items,
        [
            "name",
            "category",
            "price",
            "cost_price",
            "gross_profit",
            "gross_margin",
            "sales_count",
            "sales_amount",
            "sales_trend",
            "status",
        ],
    )
    _write_csv(
        target / "daily_revenue.csv",
        daily_revenue,
        [
            "date",
            "revenue",
            "order_count",
            "average_order_amount",
            "lunch_revenue",
            "dinner_revenue",
            "banquet_revenue",
            "lunch_orders",
            "dinner_orders",
            "family_orders",
        ],
    )
    _write_csv(
        target / "table_orders.csv",
        table_orders,
        [
            "table_name",
            "seats",
            "order_date",
            "start_time",
            "end_time",
            "duration_minutes",
            "amount",
            "order_type",
        ],
    )
    return {
        "menu_items": len(menu_items),
        "daily_revenue": len(daily_revenue),
        "table_orders": len(table_orders),
    }


if __name__ == "__main__":
    print(generate_v2())
