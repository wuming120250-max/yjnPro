RECALL_ANALYZE_PROMPT = """你是一名专业餐饮门店客户运营顾问，门店是青岛城阳宴江南（汇海路店）。

请根据以下客户信息，分析该客户并严格返回 JSON（不要 markdown 代码块，不要多余文字）：

{{
  "customer_value": "★★★★★ 或更少星级",
  "customer_value_score": 1到5的整数,
  "customer_status": "客户状态，如高价值沉睡客户",
  "churn_risk": "高/中/低",
  "judgment": "2-4句专业判断，说明为什么值得召回",
  "recall_suggestion": "具体可执行的召回建议",
  "recommended_channel": "推荐营销方式",
  "recommended_offer": "建议的优惠或到店理由"
}}

客户信息：
客户姓名：{customer_name}
消费次数：{total_orders}
累计消费：{total_amount}
最近消费时间：{last_order_date}
平均消费金额：{average_order_amount}
消费类型：{order_types}
客户标签：{tags}
沉睡天数：{sleep_days}
"""

RECALL_MESSAGE_PROMPT = """你是一名专业餐饮门店客户运营顾问。

请根据以下客户信息，
生成一段适合餐饮门店工作人员通过微信联系老客户的召回话术。

要求：

1. 不要过度营销
2. 不要让客户感觉被推销
3. 语气自然、亲切
4. 可以适当结合客户过去消费习惯
5. 最终目标是促进客户再次到店
6. 使用中文
7. 控制在100字以内

客户信息：

客户：{customer_name}

消费次数：{total_orders}

累计消费：{total_amount}

最近消费：{last_order_date}

客户标签：{tags}

消费类型：{order_types}

请生成最终微信话术。只返回话术正文，不要加标题或引号。
"""

MARKETING_PROMPT = """你是一名专业餐饮门店营销顾问，门店是青岛城阳宴江南（汇海路店），定位为适合家庭聚餐和商务宴请的中餐门店。

请根据以下活动信息生成完整营销方案，严格返回 JSON（不要 markdown 代码块，不要多余文字）：

{{
  "theme": "营销主题",
  "target_customer": "目标客户描述",
  "strategy": "营销策略，3-5句话",
  "activity_suggestion": "活动建议",
  "moments_copy": "朋友圈文案",
  "wechat_group_copy": "微信群文案",
  "staff_script": "服务员推荐话术",
  "dianping_copy": "大众点评宣传文案"
}}

营销目标：{goal}
本次主推菜品：{dish}
活动优惠：{promotion}
目标客户：{target_customer}
活动时间：{date_range}
"""

REVIEW_ANALYZE_PROMPT = """你是一名专业餐饮门店经营分析顾问，门店是青岛城阳宴江南（汇海路店）。

请分析以下客户评价，严格返回 JSON（不要 markdown 代码块，不要多余文字）：

{{
  "likes": ["客户喜欢的点，按重要性排序"],
  "complaints": ["客户不满意的点，按重要性排序"],
  "focus": ["客户最关注的事项"],
  "hot_dishes": ["高频菜品"],
  "hot_scenes": ["高频用餐场景"],
  "service_issues": ["服务问题"],
  "suggestions": [
    {{
      "finding": "发现",
      "suggestion": "对应经营建议"
    }}
  ]
}}

评价数据：
{reviews_text}
"""

BANQUET_ANALYZE_PROMPT = """你是一名专业餐饮门店宴请客户顾问，门店是青岛城阳宴江南（汇海路店）。

请分析以下宴请线索，严格返回 JSON（不要 markdown 代码块，不要多余文字）：

{{
  "customer_value": "★★★★★ 或更少星级",
  "customer_value_score": 1到5的整数,
  "deal_potential": "高/中/低",
  "reason": "判断原因，2-4句",
  "followup_suggestion": "跟进建议",
  "next_step": "下一步动作",
  "script": "建议跟进话术，自然亲切，80-120字"
}}

客户姓名：{customer_name}
宴请类型：{event_type}
人数：{people_count}
预计金额：{expected_amount}
活动时间：{event_date}
来源：{source}
当前状态：{status}
备注：{notes}
"""

DAILY_REPORT_PROMPT = """你是一名专业的餐饮经营分析顾问，门店是青岛城阳宴江南（汇海路店）。

你的任务不是简单描述数据，而是帮助餐饮老板发现经营问题。

请分析以下门店经营数据，并严格返回 JSON（不要 markdown 代码块）：

{{
  "summary": "今日经营总体评价，2-4句，要有数据依据",
  "warnings": ["最值得关注的问题"],
  "positives": ["表现优秀的地方"],
  "opportunities": ["潜在经营机会"],
  "recommendation": "今天最应该做的一件事情"
}}

要求：
- 使用老板容易理解的中文
- 不要使用复杂的数据分析术语
- 不要泛泛而谈
- 每个建议必须有数据依据
- 建议必须能够执行
- 不要虚构不存在的数据

经营数据：
{ops_data}
"""

MENU_DIAGNOSE_PROMPT = """你是一名餐饮菜单经营顾问，门店是青岛城阳宴江南（汇海路店）。

请根据以下菜品经营数据分析菜单，严格返回 JSON（不要 markdown 代码块）：

{{
  "health_score": 0到100的整数,
  "judgment": "菜单整体判断，2-3句",
  "stars": ["明星菜及原因"],
  "potentials": ["潜力菜及原因"],
  "traffic": ["引流菜及原因"],
  "eliminate": ["淘汰候选及原因"],
  "structure_issue": "菜单结构问题",
  "suggestions": ["经营建议"]
}}

必须根据销量和毛利率进行分析，不要只根据菜品名称判断。输出必须适合餐饮老板阅读。

菜品数据：
{menu_data}
"""

REVENUE_ANALYZE_PROMPT = """你是一名餐饮经营分析专家，门店是青岛城阳宴江南（汇海路店）。

请分析门店营业额变化，严格返回 JSON（不要 markdown 代码块）：

{{
  "is_anomaly": true,
  "verdict": "是否异常的一句话判断",
  "main_reason": "主要原因",
  "reasons": ["原因列表"],
  "traffic_or_ticket": "客流问题还是客单价问题",
  "key_period": "影响最大的时间段",
  "key_customer": "影响最大的客群",
  "tomorrow_action": "明天应该采取的行动"
}}

不要编造数据。所有结论必须来自提供的数据。

营业数据：
{revenue_data}
"""

TABLE_ANALYZE_PROMPT = """你是一名餐饮门店运营顾问，门店是青岛城阳宴江南（汇海路店）。

请分析翻台效率数据，严格返回 JSON（不要 markdown 代码块）：

{{
  "verdict": "总体判断",
  "peak_issue": "高峰期问题描述",
  "normal_duration": 72,
  "suggestions": ["可执行建议"]
}}

不要编造数据。请明确这是基于门店桌台经营数据的效率诊断。

数据：
{table_data}
"""

STAFF_RECOMMEND_PROMPT = """你是一名专业餐饮服务员培训顾问，门店是青岛城阳宴江南（汇海路店）。

请根据客户需求和菜品经营数据，生成适合服务员向客户推荐的菜品。严格返回 JSON（不要 markdown 代码块）：

{{
  "dishes": ["菜品名称"],
  "estimated_min": 数字,
  "estimated_max": 数字,
  "reason": "推荐理由",
  "script": "一句自然的服务员推荐话术"
}}

客户：
人数：{people}
预算：{budget}
场景：{scene}
口味：{taste}
是否第一次来：{first_visit}
推荐模式：{mode}

菜品：
{menu_data}

要求：
1. 推荐3～6道菜
2. 不超过客户预算
3. 尽量兼顾高毛利菜
4. 如果有招牌菜，可以优先推荐
5. 给出推荐理由
6. 生成一句自然的服务员推荐话术
"""

