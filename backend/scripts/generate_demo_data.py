from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

TODAY = date(2026, 8, 29)
RANDOM = random.Random(42)

SURNAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳唐罗薛伍余慕宁盛于萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵季贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万柯卢莫房缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢裴陆荣翁荀羊於惠甄")
MALE_GIVEN = ["伟", "强", "磊", "洋", "勇", "军", "杰", "涛", "超", "明", "辉", "鹏", "浩", "宇", "博", "凯", "俊", "鑫", "瑞", "宁"]
FEMALE_GIVEN = ["芳", "娜", "敏", "静", "秀英", "丽", "艳", "娟", "霞", "玲", "雪", "倩", "婷", "悦", "琳", "颖", "慧", "佳", "璐", "欣"]

ORDER_TYPES = ["普通用餐", "家庭聚餐", "朋友聚餐", "商务宴请", "生日宴", "公司聚餐"]
TABLE_TYPES = ["大厅", "窗边", "小包间", "大包间", "卡座"]
REVIEW_SOURCES = ["大众点评", "美团", "微信", "线下"]
EVENT_TYPES = ["生日宴", "家庭聚餐", "商务宴请", "公司团建", "同学聚会", "婚宴", "寿宴", "公司聚餐"]
LEAD_SOURCES = ["微信", "电话", "到店咨询", "老客户介绍", "美团"]
LEAD_STATUSES = ["待跟进", "已联系", "已报价", "已确定", "已流失", "已完成"]


def demo_dir() -> Path:
    docker_data = Path("/app/data/demo")
    if Path("/app/data").exists() or Path(__file__).resolve().as_posix().startswith("/app/"):
        docker_data.mkdir(parents=True, exist_ok=True)
        return docker_data
    repo_data = Path(__file__).resolve().parents[2] / "data" / "demo"
    repo_data.mkdir(parents=True, exist_ok=True)
    return repo_data


def compute_level(total_amount: float, total_orders: int, last_order_date: date) -> str:
    days = (TODAY - last_order_date).days
    high_value = total_amount >= 2000 or total_orders >= 5
    sleeping = days >= 60
    if high_value and sleeping:
        return "高价值沉睡客户"
    if sleeping:
        return "沉睡客户"
    if high_value:
        return "高价值客户"
    if total_orders >= 2 or total_amount >= 800:
        return "潜力客户"
    return "普通客户"


def phone_at(index: int) -> str:
    return f"138{index:08d}"


def split_amount(total: float, count: int) -> list[float]:
    if count <= 1:
        return [round(total, 2)]
    weights = [RANDOM.randint(8, 18) for _ in range(count)]
    total_weight = sum(weights)
    amounts = [round(total * w / total_weight, 2) for w in weights]
    amounts[-1] = round(total - sum(amounts[:-1]), 2)
    return [max(68.0, amt) for amt in amounts]


def order_dates(last_date: date, count: int, prefer_recent: bool = False) -> list[date]:
    dates = [last_date]
    cursor = last_date
    for _ in range(count - 1):
        gap = RANDOM.randint(3, 18) if prefer_recent else RANDOM.randint(8, 45)
        cursor = cursor - timedelta(days=gap)
        if cursor.year < 2024:
            cursor = date(2024, RANDOM.randint(1, 12), RANDOM.randint(1, 28))
        dates.append(cursor)
    return dates


def make_special_customers() -> list[dict]:
    specials = [
        {
            "customer_name": "赵女士",
            "gender": "女",
            "age": 38,
            "total_orders": 9,
            "total_amount": 4260,
            "sleep_days": 95,
            "tags": "高价值,家庭聚餐",
            "preferred_type": "家庭聚餐",
        },
        {
            "customer_name": "张先生",
            "gender": "男",
            "age": 42,
            "total_orders": 7,
            "total_amount": 3180,
            "sleep_days": 78,
            "tags": "商务宴请,高价值",
            "preferred_type": "商务宴请",
        },
        {"customer_name": "王先生", "gender": "男", "age": 45, "total_orders": 8, "total_amount": 3520, "sleep_days": 88, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
        {"customer_name": "李女士", "gender": "女", "age": 36, "total_orders": 6, "total_amount": 2680, "sleep_days": 71, "tags": "高价值,生日宴", "preferred_type": "生日宴"},
        {"customer_name": "刘先生", "gender": "男", "age": 48, "total_orders": 10, "total_amount": 5100, "sleep_days": 102, "tags": "高价值,商务宴请", "preferred_type": "商务宴请"},
        {"customer_name": "陈女士", "gender": "女", "age": 41, "total_orders": 5, "total_amount": 2340, "sleep_days": 65, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
        {"customer_name": "杨先生", "gender": "男", "age": 50, "total_orders": 12, "total_amount": 6800, "sleep_days": 110, "tags": "高价值,公司聚餐", "preferred_type": "公司聚餐"},
        {"customer_name": "黄女士", "gender": "女", "age": 34, "total_orders": 7, "total_amount": 2890, "sleep_days": 82, "tags": "高价值,朋友聚餐", "preferred_type": "朋友聚餐"},
        {"customer_name": "周先生", "gender": "男", "age": 39, "total_orders": 9, "total_amount": 4450, "sleep_days": 91, "tags": "高价值,商务宴请", "preferred_type": "商务宴请"},
        {"customer_name": "吴女士", "gender": "女", "age": 37, "total_orders": 6, "total_amount": 2510, "sleep_days": 68, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
        {"customer_name": "徐先生", "gender": "男", "age": 44, "total_orders": 8, "total_amount": 3920, "sleep_days": 77, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
        {"customer_name": "孙女士", "gender": "女", "age": 55, "total_orders": 11, "total_amount": 5600, "sleep_days": 120, "tags": "高价值,寿宴", "preferred_type": "家庭聚餐"},
        {"customer_name": "马先生", "gender": "男", "age": 33, "total_orders": 5, "total_amount": 2180, "sleep_days": 63, "tags": "高价值,普通用餐", "preferred_type": "普通用餐"},
        {"customer_name": "朱女士", "gender": "女", "age": 40, "total_orders": 7, "total_amount": 3300, "sleep_days": 85, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
        {"customer_name": "胡先生", "gender": "男", "age": 46, "total_orders": 6, "total_amount": 2750, "sleep_days": 73, "tags": "高价值,商务宴请", "preferred_type": "商务宴请"},
        {"customer_name": "郭女士", "gender": "女", "age": 32, "total_orders": 8, "total_amount": 4100, "sleep_days": 98, "tags": "高价值,生日宴", "preferred_type": "生日宴"},
        {"customer_name": "何先生", "gender": "男", "age": 35, "total_orders": 9, "total_amount": 3890, "sleep_days": 80, "tags": "高价值,朋友聚餐", "preferred_type": "朋友聚餐"},
        {"customer_name": "高女士", "gender": "女", "age": 43, "total_orders": 5, "total_amount": 2050, "sleep_days": 61, "tags": "高价值,家庭聚餐", "preferred_type": "家庭聚餐"},
    ]
    customers = []
    for idx, item in enumerate(specials, start=1):
        last_order_date = TODAY - timedelta(days=item["sleep_days"])
        birthday = date(2026 - item["age"], RANDOM.randint(1, 12), RANDOM.randint(1, 28))
        customers.append(
            {
                "customer_name": item["customer_name"],
                "phone": phone_at(idx),
                "gender": item["gender"],
                "age": item["age"],
                "total_orders": item["total_orders"],
                "total_amount": item["total_amount"],
                "last_order_date": last_order_date,
                "average_order_amount": round(item["total_amount"] / item["total_orders"], 2),
                "birthday": birthday,
                "tags": item["tags"],
                "preferred_type": item["preferred_type"],
                "customer_level": compute_level(item["total_amount"], item["total_orders"], last_order_date),
            }
        )
    return customers


def random_name(gender: str, used: set[str]) -> str:
    title = "先生" if gender == "男" else "女士"
    given_pool = MALE_GIVEN if gender == "男" else FEMALE_GIVEN
    for _ in range(50):
        name = RANDOM.choice(SURNAMES) + title
        if name not in used:
            used.add(name)
            return name
    name = RANDOM.choice(SURNAMES) + RANDOM.choice(given_pool) + title
    used.add(name)
    return name


def build_customers() -> list[dict]:
    used_names = {"赵女士", "张先生"}
    customers = make_special_customers()

    profiles = (
        [{"kind": "high_active"}] * 36
        + [{"kind": "sleeping"}] * 32
        + [{"kind": "potential"}] * 42
        + [{"kind": "normal"}] * (200 - len(customers) - 36 - 32 - 42)
    )
    RANDOM.shuffle(profiles)

    for offset, profile in enumerate(profiles, start=len(customers) + 1):
        gender = RANDOM.choice(["男", "女"])
        name = random_name(gender, used_names)
        age = RANDOM.randint(26, 58)
        kind = profile["kind"]
        preferred = RANDOM.choice(ORDER_TYPES)
        if kind == "high_active":
            total_orders = RANDOM.randint(5, 14)
            avg = RANDOM.randint(280, 680)
            last = TODAY - timedelta(days=RANDOM.choice([0, 0, 1, 2, 3, 5, 8, 12, 20, 28]))
            tags = f"高价值,{preferred}"
        elif kind == "sleeping":
            total_orders = RANDOM.randint(1, 4)
            avg = RANDOM.randint(160, 380)
            last = TODAY - timedelta(days=RANDOM.randint(60, 140))
            tags = preferred
        elif kind == "potential":
            total_orders = RANDOM.randint(2, 4)
            avg = RANDOM.randint(220, 480)
            last = TODAY - timedelta(days=RANDOM.randint(5, 45))
            tags = f"潜力客户,{preferred}"
        else:
            total_orders = RANDOM.randint(1, 2)
            avg = RANDOM.randint(120, 280)
            last = TODAY - timedelta(days=RANDOM.randint(3, 50))
            tags = preferred
        total_amount = round(total_orders * avg + RANDOM.randint(-40, 80), 2)
        total_amount = max(total_amount, 88)
        birthday = date(2026 - age, RANDOM.randint(1, 12), RANDOM.randint(1, 28))
        customers.append(
            {
                "customer_name": name,
                "phone": phone_at(offset),
                "gender": gender,
                "age": age,
                "total_orders": total_orders,
                "total_amount": round(total_amount, 2),
                "last_order_date": last,
                "average_order_amount": round(total_amount / total_orders, 2),
                "birthday": birthday,
                "tags": tags,
                "preferred_type": preferred,
                "customer_level": compute_level(total_amount, total_orders, last),
            }
        )
    return customers


def build_orders(customers: list[dict]) -> list[dict]:
    orders: list[dict] = []
    seq = 1
    for index, customer in enumerate(customers, start=1):
        count = customer["total_orders"]
        amounts = split_amount(customer["total_amount"], count)
        prefer_recent = (TODAY - customer["last_order_date"]).days < 30
        dates = order_dates(customer["last_order_date"], count, prefer_recent=prefer_recent)
        for amount, order_date in zip(amounts, dates):
            preferred = customer["preferred_type"]
            order_type = preferred if RANDOM.random() < 0.6 else RANDOM.choice(ORDER_TYPES)
            people = 8 if order_type in {"商务宴请", "公司聚餐"} else RANDOM.choice([2, 3, 4, 5, 6, 8])
            table = "大包间" if people >= 8 else ("小包间" if people >= 5 else RANDOM.choice(TABLE_TYPES))
            orders.append(
                {
                    "customer_index": index,
                    "order_no": f"YJN{order_date.strftime('%Y%m%d')}{seq:04d}",
                    "order_date": order_date,
                    "amount": amount,
                    "people_count": people,
                    "order_type": order_type,
                    "table_type": table,
                }
            )
            seq += 1

    active_indexes = [
        idx
        for idx, customer in enumerate(customers, start=1)
        if (TODAY - customer["last_order_date"]).days < 60
    ]
    while len(orders) < 1000 and active_indexes:
        customer_index = RANDOM.choice(active_indexes)
        customer = customers[customer_index - 1]
        extra_date = TODAY - timedelta(days=RANDOM.randint(0, 6))
        if extra_date > customer["last_order_date"]:
            extra_date = customer["last_order_date"]
        amount = round(RANDOM.uniform(168, 688), 2)
        order_type = customer["preferred_type"]
        people = RANDOM.choice([2, 3, 4, 5, 6])
        orders.append(
            {
                "customer_index": customer_index,
                "order_no": f"YJNextra{seq:05d}",
                "order_date": extra_date,
                "amount": amount,
                "people_count": people,
                "order_type": order_type,
                "table_type": RANDOM.choice(TABLE_TYPES),
            }
        )
        customer["total_orders"] += 1
        customer["total_amount"] = round(customer["total_amount"] + amount, 2)
        customer["average_order_amount"] = round(customer["total_amount"] / customer["total_orders"], 2)
        customer["customer_level"] = compute_level(
            customer["total_amount"], customer["total_orders"], customer["last_order_date"]
        )
        seq += 1

    today_count = sum(1 for item in orders if item["order_date"] == TODAY)
    if today_count < 40:
        for customer_index in active_indexes:
            if today_count >= 55:
                break
            customer = customers[customer_index - 1]
            if (TODAY - customer["last_order_date"]).days > 7:
                continue
            amount = round(RANDOM.uniform(188, 520), 2)
            orders.append(
                {
                    "customer_index": customer_index,
                    "order_no": f"YJNtoday{seq:05d}",
                    "order_date": TODAY,
                    "amount": amount,
                    "people_count": RANDOM.choice([2, 3, 4, 5]),
                    "order_type": customer["preferred_type"],
                    "table_type": RANDOM.choice(["大厅", "卡座", "窗边"]),
                }
            )
            customer["last_order_date"] = TODAY
            customer["total_orders"] += 1
            customer["total_amount"] = round(customer["total_amount"] + amount, 2)
            customer["average_order_amount"] = round(customer["total_amount"] / customer["total_orders"], 2)
            customer["customer_level"] = compute_level(
                customer["total_amount"], customer["total_orders"], customer["last_order_date"]
            )
            seq += 1
            today_count += 1
    return orders


def build_reviews(customers: list[dict]) -> list[dict]:
    positives = [
        ("海鲜很新鲜，清蒸鲈鱼做得正好，家人都说好吃。", "好评", "海鲜,菜品口味,家庭聚餐", 5),
        ("环境干净上档次，包间安静，很适合家庭聚餐。", "好评", "环境,家庭聚餐", 5),
        ("红烧肉入口即化，服务员介绍得很仔细。", "好评", "菜品口味,服务", 5),
        ("蒜蓉粉丝扇贝很赞，海鲜新鲜，会再来。", "好评", "海鲜,菜品口味", 5),
        ("朋友聚餐选这里很合适，菜品丰富，分量也够。", "好评", "朋友聚餐,菜品口味", 4),
        ("商务招待用地不错，包间私密，菜品摆盘好看。", "好评", "商务宴请,环境", 5),
        ("孩子过生日订了小包间，店里还准备了寿面，很贴心。", "好评", "生日宴,服务", 5),
        ("汇海路这家宴江南停车还算方便，味道稳定。", "好评", "环境,菜品口味", 4),
        ("清蒸海鲜很鲜，配菜也入味，适合一家人吃饭。", "好评", "海鲜,家庭聚餐", 5),
        ("服务态度好，上菜节奏周末白天也还行。", "好评", "服务", 4),
    ]
    mixed = [
        ("菜很好吃，就是周末晚上有点慢。", "中评", "菜品口味,上菜速度", 3),
        ("环境不错，个别菜价格偏高。", "中评", "环境,价格", 3),
        ("味道可以，高峰期服务员有点忙不过来。", "中评", "菜品口味,服务响应", 3),
    ]
    negatives = [
        ("周六晚餐等位加上上菜，等了挺久，希望高峰期能快一点。", "差评", "上菜速度,高峰期", 2),
        ("菜品整体还行，但服务员叫了两次才过来加茶。", "差评", "服务响应,高峰期", 2),
        ("有的海鲜小贵，性价比一般。", "差评", "价格,海鲜", 2),
        ("周末人太多，上菜慢，带老人吃饭有点着急。", "差评", "上菜速度,家庭聚餐", 2),
    ]
    reviews = []
    for i in range(100):
        if i < 72:
            content, sentiment, tags, rating = RANDOM.choice(positives)
            rating = rating if RANDOM.random() > 0.15 else 4
        elif i < 88:
            content, sentiment, tags, rating = RANDOM.choice(mixed)
        else:
            content, sentiment, tags, rating = RANDOM.choice(negatives)
        customer = RANDOM.choice(customers)
        reviews.append(
            {
                "customer_name": customer["customer_name"],
                "rating": rating,
                "content": content,
                "review_date": TODAY - timedelta(days=RANDOM.randint(1, 90)),
                "source": RANDOM.choice(REVIEW_SOURCES),
                "tags": tags,
                "sentiment": sentiment,
            }
        )
    reviews.sort(key=lambda item: item["review_date"], reverse=True)
    return reviews


def build_leads(customers: list[dict]) -> list[dict]:
    leads = [
        {
            "customer_name": "张先生",
            "phone": "13800000002",
            "event_type": "公司聚餐",
            "people_count": 25,
            "expected_amount": "5000-8000",
            "event_date": date(2026, 9, 12),
            "source": "微信",
            "status": "待跟进",
            "notes": "公司聚餐，预算明确，希望要安静包间，有海鲜。",
        }
    ]
    samples = [
        ("李女士", "生日宴", 12, "2000-3500", "待跟进"),
        ("王总", "商务宴请", 8, "3000-5000", "已联系"),
        ("陈先生", "同学聚会", 18, "4000-6000", "已报价"),
        ("刘女士", "家庭聚餐", 10, "1500-2500", "待跟进"),
        ("周总", "公司团建", 30, "8000-12000", "已联系"),
        ("孙女士", "寿宴", 20, "5000-7000", "已确定"),
        ("吴先生", "婚宴", 40, "15000-20000", "已报价"),
        ("郑女士", "家庭聚餐", 6, "800-1500", "已完成"),
        ("冯先生", "商务宴请", 6, "2000-3000", "已流失"),
        ("何女士", "生日宴", 8, "1200-2000", "待跟进"),
    ]
    used = {"张先生"}
    idx = 3
    for name, event_type, people, amount, status in samples:
        leads.append(
            {
                "customer_name": name,
                "phone": phone_at(200 + idx),
                "event_type": event_type,
                "people_count": people,
                "expected_amount": amount,
                "event_date": TODAY + timedelta(days=RANDOM.randint(5, 40)),
                "source": RANDOM.choice(LEAD_SOURCES),
                "status": status,
                "notes": f"{event_type}咨询，人数约{people}人。",
            }
        )
        used.add(name)
        idx += 1

    while len(leads) < 30:
        gender = RANDOM.choice(["男", "女"])
        name = random_name(gender, used)
        event_type = RANDOM.choice(EVENT_TYPES)
        people = RANDOM.choice([6, 8, 10, 12, 15, 18, 20, 22, 25, 28])
        low = people * RANDOM.randint(180, 280)
        high = people * RANDOM.randint(300, 420)
        leads.append(
            {
                "customer_name": name,
                "phone": phone_at(260 + len(leads)),
                "event_type": event_type,
                "people_count": people,
                "expected_amount": f"{low}-{high}",
                "event_date": TODAY + timedelta(days=RANDOM.randint(3, 50)),
                "source": RANDOM.choice(LEAD_SOURCES),
                "status": RANDOM.choice(LEAD_STATUSES),
                "notes": "",
            }
        )
    return leads


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output = {}
            for key in fieldnames:
                value = row[key]
                output[key] = value.isoformat() if isinstance(value, date) else value
            writer.writerow(output)


def generate_all(output_dir: Path | None = None) -> dict[str, int]:
    target = output_dir or demo_dir()
    customers = build_customers()
    orders = build_orders(customers)
    reviews = build_reviews(customers)
    leads = build_leads(customers)

    write_csv(
        target / "customers.csv",
        customers,
        [
            "customer_name",
            "phone",
            "gender",
            "age",
            "customer_level",
            "total_orders",
            "total_amount",
            "last_order_date",
            "average_order_amount",
            "birthday",
            "tags",
            "preferred_type",
        ],
    )
    write_csv(
        target / "orders.csv",
        orders,
        [
            "customer_index",
            "order_no",
            "order_date",
            "amount",
            "people_count",
            "order_type",
            "table_type",
        ],
    )
    write_csv(
        target / "reviews.csv",
        reviews,
        ["customer_name", "rating", "content", "review_date", "source", "tags", "sentiment"],
    )
    write_csv(
        target / "banquet_leads.csv",
        leads,
        [
            "customer_name",
            "phone",
            "event_type",
            "people_count",
            "expected_amount",
            "event_date",
            "source",
            "status",
            "notes",
        ],
    )
    return {
        "customers": len(customers),
        "orders": len(orders),
        "reviews": len(reviews),
        "banquet_leads": len(leads),
    }


if __name__ == "__main__":
    counts = generate_all()
    print(counts)
