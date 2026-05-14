import type { AgentRun } from "../../api/client";
import { ImprovementPolicyBadge } from "./ImprovementPolicyBadge";

interface AgentRunTableProps {
  runs: AgentRun[];
}

export function AgentRunTable({ runs }: AgentRunTableProps) {
  return (
    <div className="overflow-hidden rounded border border-line bg-panel shadow-soft">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-white/5 text-slate-300">
          <tr>
            <th className="px-4 py-3 font-medium">Thời gian</th>
            <th className="px-4 py-3 font-medium">Tác vụ</th>
            <th className="px-4 py-3 font-medium">Tác nhân</th>
            <th className="px-4 py-3 font-medium">Trạng thái</th>
            <th className="px-4 py-3 font-medium">Điểm</th>
            <th className="px-4 py-3 font-medium">Thời gian chạy</th>
            <th className="px-4 py-3 font-medium">Lỗi</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="border-t border-line align-top">
              <td className="whitespace-nowrap px-4 py-4 text-slate-300">{new Date(run.created_at).toLocaleString("vi-VN")}</td>
              <td className="max-w-[280px] px-4 py-4 text-white">{run.task}</td>
              <td className="whitespace-nowrap px-4 py-4 text-slate-200">{run.agent_name}</td>
              <td className="px-4 py-4">
                <ImprovementPolicyBadge value={run.status} />
              </td>
              <td className="whitespace-nowrap px-4 py-4 text-slate-200">{run.score ?? "Không có"}</td>
              <td className="whitespace-nowrap px-4 py-4 text-slate-300">{run.runtime_ms ? `${run.runtime_ms} ms` : "Không có"}</td>
              <td className="max-w-[260px] px-4 py-4 text-slate-400">{run.error_message || ""}</td>
            </tr>
          ))}
          {!runs.length ? (
            <tr>
              <td className="px-4 py-8 text-center text-slate-400" colSpan={7}>
                Chưa có lượt chạy tác nhân.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
