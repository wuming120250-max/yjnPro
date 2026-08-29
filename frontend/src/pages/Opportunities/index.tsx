import { Alert, Button, Col, Empty, Row, Spin, message } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  analyzeOpportunity,
  completeOpportunity,
  fetchOpportunities,
  generateOpportunities,
  ignoreOpportunity,
  processOpportunity,
} from "../../api/opportunities";
import { AI_UNAVAILABLE, getErrorMessage } from "../../api/client";
import PageHeader from "../../components/PageHeader";
import type { OpportunityItem, OpportunityListResponse } from "../../types";
import OpportunityCard from "./OpportunityCard";
import OpportunityDetail from "./OpportunityDetail";
import OpportunityFilter from "./OpportunityFilter";
import OpportunityStats from "./OpportunityStats";
import TodayPriority from "./TodayPriority";

const EMPTY_STATS = { total: 0, high: 0, medium: 0, low: 0, completed: 0, pending: 0, processing: 0 };

export default function Opportunities() {
  const navigate = useNavigate();
  const [data, setData] = useState<OpportunityListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [type, setType] = useState("");
  const [level, setLevel] = useState("");
  const [current, setCurrent] = useState<OpportunityItem | null>(null);

  const load = async () => {
    const result = await fetchOpportunities({
      type: type || undefined,
      level: level || undefined,
    });
    setData(result);
    return result;
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const result = await fetchOpportunities({
          type: type || undefined,
          level: level || undefined,
        });
        if (cancelled) return;
        setData(result);
        setError("");
        if (result.total === 0 && !type && !level) {
          setGenerating(true);
          const generated = await generateOpportunities(false);
          if (!cancelled) setData(generated);
        }
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err, "经营机会加载失败"));
      } finally {
        if (!cancelled) {
          setGenerating(false);
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [type, level]);

  const refreshItem = (item: OpportunityItem) => {
    setCurrent(item);
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        items: prev.items.map((row) => (row.id === item.id ? item : row)),
        today_priority: prev.today_priority?.id === item.id ? item : prev.today_priority,
      };
    });
  };

  const visible = useMemo(() => data?.items || [], [data]);

  return (
    <div>
      <PageHeader
        title="AI经营机会中心"
        extra={
          <Button
            type="primary"
            loading={generating}
            onClick={async () => {
              setGenerating(true);
              try {
                setData(await generateOpportunities(true));
                setError("");
              } catch (err) {
                setError(getErrorMessage(err, AI_UNAVAILABLE));
              } finally {
                setGenerating(false);
              }
            }}
          >
            生成今日机会
          </Button>
        }
      >
        不要自己翻多个页面。每天先看：现在最值得做什么。
      </PageHeader>
      {generating ? <Alert type="info" showIcon message="AI正在分析经营数据..." style={{ marginBottom: 16 }} /> : null}
      {error ? <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} /> : null}
      {loading && !data ? <Spin /> : null}
      {data ? (
        <>
          <OpportunityStats stats={data.stats || EMPTY_STATS} bizDate={data.biz_date} demoMode={data.demo_mode} />
          <div style={{ marginTop: 16 }}>
            <TodayPriority
              item={data.today_priority}
              onOpen={setCurrent}
              onCreate={async (item) => {
                try {
                  refreshItem(await processOpportunity(item.id));
                  message.success("已创建为今日任务（处理中）");
                } catch (err) {
                  message.error(getErrorMessage(err, "更新失败"));
                }
              }}
            />
          </div>
          <OpportunityFilter type={type} level={level} onChange={(next) => { setType(next.type); setLevel(next.level); }} />
          {visible.length ? (
            <Row gutter={[16, 16]}>
              {visible.map((item) => (
                <Col xs={24} md={12} xl={8} key={item.id}>
                  <OpportunityCard item={item} onOpen={setCurrent} />
                </Col>
              ))}
            </Row>
          ) : (
            <Empty description="暂无匹配机会" />
          )}
        </>
      ) : null}
      <OpportunityDetail
        item={current}
        open={Boolean(current)}
        analyzing={analyzing}
        onClose={() => setCurrent(null)}
        onAnalyze={async () => {
          if (!current) return;
          setAnalyzing(true);
          try {
            refreshItem(await analyzeOpportunity(current.id));
          } catch (err) {
            message.error(getErrorMessage(err, AI_UNAVAILABLE));
          } finally {
            setAnalyzing(false);
          }
        }}
        onProcess={async () => {
          if (!current) return;
          refreshItem(await processOpportunity(current.id));
        }}
        onComplete={async () => {
          if (!current) return;
          refreshItem(await completeOpportunity(current.id));
          void load();
        }}
        onIgnore={async () => {
          if (!current) return;
          refreshItem(await ignoreOpportunity(current.id));
          setCurrent(null);
          void load();
        }}
        onJump={(path) => navigate(path)}
      />
    </div>
  );
}
