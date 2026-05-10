import { BookOpen, GitPullRequest, ListChecks, Percent, Sparkles, Trophy } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  getSelfImprovementSummary,
  listAgentRuns,
  listImprovementLessons,
  type AgentRun,
  type ImprovementLesson,
  type SelfImprovementSummary
} from "../api/client";
import { ImprovementPolicyBadge } from "../components/self-improvement/ImprovementPolicyBadge";
import { ScoreCard } from "../components/self-improvement/ScoreCard";

interface AgentStat {
  agent: string;
  averageScore: number;
  failures: number;
  total: number;
}

export function SelfImprovementDashboard() {
  const [summary, setSummary] = useState<SelfImprovementSummary | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [lessons, setLessons] = useState<ImprovementLesson[]>([]);

  useEffect(() => {
    void Promise.all([
      getSelfImprovementSummary().then(setSummary),
      listAgentRuns({ limit: 200 }).then(setRuns),
      listImprovementLessons({ status: "active" }).then(setLessons)
    ]).catch(() => {
      setSummary(null);
      setRuns([]);
      setLessons([]);
    });
  }, []);

  const stats = useMemo<AgentStat[]>(() => {
    const byAgent = new Map<string, { total: number; failures: number; score: number; scored: number }>();
    for (const run of runs) {
      const current = byAgent.get(run.agent_name) ?? { total: 0, failures: 0, score: 0, scored: 0 };
      current.total += 1;
      if (run.status === "failed") current.failures += 1;
      if (typeof run.score === "number") {
        current.score += run.score;
        current.scored += 1;
      }
      byAgent.set(run.agent_name, current);
    }
    return Array.from(byAgent.entries()).map(([agent, value]) => ({
      agent,
      averageScore: value.scored ? Number((value.score / value.scored).toFixed(2)) : 0,
      failures: value.failures,
      total: value.total
    }));
  }, [runs]);

  const topAgents = [...stats].sort((a, b) => b.averageScore - a.averageScore).slice(0, 5);
  const failureAgents = [...stats].sort((a, b) => b.failures - a.failures).slice(0, 5);
  const latestLessons = lessons.slice(0, 5);

  const cards = [
    { label: "Tổng lượt chạy", value: summary?.total_runs ?? 0, icon: ListChecks },
    { label: "Điểm trung bình", value: summary?.average_score ?? 0, icon: Trophy },
    { label: "Tỷ lệ thành công", value: `${summary?.success_rate ?? 0}%`, icon: Percent },
    { label: "Bài học", value: summary?.total_lessons ?? 0, icon: BookOpen },
    { label: "Phiên bản lời nhắc", value: summary?.total_prompt_versions ?? 0, icon: Sparkles },
    { label: "Gợi ý quy trình đang chờ", value: summary?.pending_workflow_suggestions ?? 0, icon: GitPullRequest }
  ];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Tự cải thiện</h1>
        <p className="mt-1 text-sm text-slate-400">Đánh giá tác nhân, bài học, phiên bản lời nhắc và gợi ý quy trình</p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <ScoreCard key={card.label} label={card.label} value={card.value} icon={card.icon} />
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="rounded border border-line bg-panel p-5 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Tác nhân có điểm cao nhất</h2>
          <div className="mt-4 overflow-hidden rounded border border-line">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="px-4 py-3 font-medium">Tác nhân</th>
                  <th className="px-4 py-3 font-medium">Trung bình</th>
                  <th className="px-4 py-3 font-medium">Lượt chạy</th>
                </tr>
              </thead>
              <tbody>
                {topAgents.map((agent) => (
                  <tr key={agent.agent} className="border-t border-line">
                    <td className="px-4 py-3 text-white">{agent.agent}</td>
                    <td className="px-4 py-3 text-slate-200">{agent.averageScore}</td>
                    <td className="px-4 py-3 text-slate-300">{agent.total}</td>
                  </tr>
                ))}
                {!topAgents.length ? (
                  <tr>
                    <td className="px-4 py-6 text-center text-slate-400" colSpan={3}>
                      Chưa có lượt chạy được chấm điểm.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded border border-line bg-panel p-5 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Tác nhân lỗi nhiều nhất</h2>
          <div className="mt-4 overflow-hidden rounded border border-line">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="px-4 py-3 font-medium">Tác nhân</th>
                  <th className="px-4 py-3 font-medium">Số lỗi</th>
                  <th className="px-4 py-3 font-medium">Lượt chạy</th>
                </tr>
              </thead>
              <tbody>
                {failureAgents.map((agent) => (
                  <tr key={agent.agent} className="border-t border-line">
                    <td className="px-4 py-3 text-white">{agent.agent}</td>
                    <td className="px-4 py-3 text-slate-200">{agent.failures}</td>
                    <td className="px-4 py-3 text-slate-300">{agent.total}</td>
                  </tr>
                ))}
                {!failureAgents.length ? (
                  <tr>
                    <td className="px-4 py-6 text-center text-slate-400" colSpan={3}>
                      Chưa có lượt chạy thất bại.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="rounded border border-line bg-panel p-5 shadow-soft">
        <h2 className="text-lg font-semibold text-white">Bài học mới nhất</h2>
        <div className="mt-4 space-y-3">
          {latestLessons.map((lesson) => (
            <div key={lesson.id} className="rounded border border-line bg-ink p-4">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-white">{lesson.title}</p>
                <ImprovementPolicyBadge value={lesson.lesson_type} />
              </div>
              <p className="mt-2 line-clamp-2 text-sm text-slate-400">{lesson.content}</p>
            </div>
          ))}
          {!latestLessons.length ? <p className="text-sm text-slate-400">Chưa có bài học.</p> : null}
        </div>
      </section>
    </div>
  );
}
