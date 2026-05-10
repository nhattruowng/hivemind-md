import {
  Activity,
  BrainCircuit,
  Clock3,
  Database,
  FileText,
  Filter,
  Gauge,
  Loader2,
  RefreshCw,
  Route,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  type LucideIcon
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { chat, cleanupKnowledge, type AgentLog, type ChatResponse, type KnowledgeCleanupResponse } from "../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  meta?: ChatResponse;
}

const thinkingRoles = [
  { stage: "input", name: "Input Router", description: "Chuẩn hóa câu hỏi và giảm token nhiễu.", icon: BrainCircuit },
  { stage: "route", name: "Knowledge Router", description: "Phân cấp câu hỏi tới folder tri thức phù hợp.", icon: Route },
  { stage: "plan", name: "Planner", description: "Chia request thành bước, intent, risk và quyền chạy.", icon: CheckCircle2 },
  { stage: "answer", name: "Retrieval Answer", description: "Tìm chunk phù hợp trong vector store.", icon: Search },
  { stage: "refresh", name: "Auto Research", description: "Search và cập nhật kho nếu thiếu tri thức.", icon: Sparkles },
  { stage: "verify", name: "Verifier", description: "Kiểm tra grounding và citation trước khi trả lời.", icon: ShieldCheck },
  { stage: "quality", name: "Quality Critic", description: "Chấm độ tin cậy và lọc nguồn yếu.", icon: ShieldCheck },
  { stage: "memory", name: "Chat Memory", description: "Lưu phiên trò chuyện thành Markdown.", icon: Database }
];

export function ChatWithKnowledge() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [cleanupResult, setCleanupResult] = useState<KnowledgeCleanupResponse | null>(null);

  const latestMeta = useMemo(() => {
    for (let index = messages.length - 1; index >= 0; index -= 1) {
      const meta = messages[index].meta;
      if (meta) return meta;
    }
    return null;
  }, [messages]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const question = input.trim();
    if (!question) return;
    setInput("");
    setMessages((current) => [...current, { role: "user", content: question }]);
    setLoading(true);
    try {
      const answer = await chat({
        message: question,
        conversation_id: conversationId,
        auto_refresh: true,
        category: "chat-auto",
        mode: "quick"
      });
      setConversationId(answer.conversation_id);
      setMessages((current) => [...current, { role: "assistant", content: answer.answer, meta: answer }]);
    } catch (err) {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: err instanceof Error ? err.message : "Không gửi được yêu cầu chat" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const runCleanup = async () => {
    const approved = window.confirm("Cleanup sẽ chuyển file nhiễu/trùng vào quarantine. Tiếp tục?");
    if (!approved) return;
    setCleanupLoading(true);
    try {
      const result = await cleanupKnowledge({ dry_run: false, min_trust: 0.2, approved: true });
      setCleanupResult(result);
    } finally {
      setCleanupLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-2.5rem)] flex-col gap-5">
      <header className="rounded border border-line bg-panel p-5 shadow-soft">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div className="min-w-0">
            <div className="inline-flex items-center gap-2 rounded border border-signal/30 bg-signal/10 px-2.5 py-1 text-xs font-semibold text-signal">
              <BrainCircuit size={14} aria-hidden="true" />
              Knowledge Chat
            </div>
            <h1 className="mt-3 text-2xl font-semibold text-white">Trò chuyện với kho tri thức</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Chat lưu lịch sử Markdown, tự bổ sung tri thức khi thiếu dữ liệu và hiển thị từng agent đang tham gia.
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-3 xl:min-w-[520px]">
            <Metric icon={Activity} label="Agent" value={String(latestMeta?.active_agents ?? (loading ? thinkingRoles.length : 0))} />
            <Metric icon={Gauge} label="Confidence" value={latestMeta?.confidence != null ? `${Math.round(latestMeta.confidence * 100)}%` : "N/A"} />
            <Metric icon={FileText} label="Chat MD" value={latestMeta?.chat_file ? "saved" : "none"} />
          </div>
        </div>
      </header>

      <main className="grid min-h-0 flex-1 gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <section className="flex min-h-[620px] flex-col rounded border border-line bg-panel shadow-soft">
          <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
            <div>
              <h2 className="text-sm font-semibold text-white">Conversation</h2>
              <p className="mt-1 text-xs text-slate-500">{conversationId ? `Session ${conversationId}` : "Session mới"}</p>
            </div>
            {latestMeta?.auto_refreshed ? (
              <span className="inline-flex items-center gap-2 rounded border border-accent/30 bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
                <RefreshCw size={13} aria-hidden="true" />
                Đã cập nhật kho
              </span>
            ) : null}
          </div>

          <div className="flex-1 overflow-auto p-4 scrollbar-thin">
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="rounded border border-dashed border-line p-6 text-sm text-slate-400">
                  Chưa có tin nhắn.
                </div>
              ) : null}
              {messages.map((message, index) => (
                <ChatBubble key={`${message.role}-${index}`} message={message} />
              ))}
              {loading ? <ThinkingBubble /> : null}
            </div>
          </div>

          <form onSubmit={submit} className="flex gap-2 border-t border-line bg-ink/70 p-3">
            <textarea
              className="min-h-12 flex-1 resize-none rounded border border-line bg-ink px-3 py-3 text-sm leading-6 text-white"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Hỏi về tri thức đã lưu..."
              rows={2}
            />
            <button
              className="inline-flex min-h-12 shrink-0 items-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-50"
              disabled={loading || !input.trim()}
              type="submit"
            >
              {loading ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : <Send size={18} aria-hidden="true" />}
              Gửi
            </button>
          </form>
        </section>

        <aside className="space-y-4">
          <AgentThinkingPanel loading={loading} meta={latestMeta} />

          <section className="rounded border border-line bg-panel p-4 shadow-soft">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold text-white">Knowledge cleanup</h2>
                <p className="mt-1 text-xs leading-5 text-slate-400">Cụm agent thủ công quét trùng lặp, nguồn yếu và rebuild map.</p>
              </div>
              <button
                className="inline-flex min-h-9 shrink-0 items-center gap-2 rounded border border-signal px-3 text-xs font-semibold text-signal hover:bg-signal/10 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={cleanupLoading}
                type="button"
                onClick={() => void runCleanup()}
              >
                {cleanupLoading ? <Loader2 size={15} className="animate-spin" aria-hidden="true" /> : <Filter size={15} aria-hidden="true" />}
                Làm sạch
              </button>
            </div>
            {cleanupResult ? <CleanupResultPanel result={cleanupResult} /> : null}
          </section>
        </aside>
      </main>
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-ink px-3 py-2">
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Icon size={14} className="text-signal" aria-hidden="true" />
        {label}
      </div>
      <div className="mt-1 truncate text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <article className={["flex", isUser ? "justify-end" : "justify-start"].join(" ")}>
      <div
        className={[
          "w-full max-w-[880px] rounded border p-4 text-sm leading-7",
          isUser ? "border-signal/30 bg-signal/10 md:max-w-[70%]" : "border-line bg-ink"
        ].join(" ")}
      >
        <div className="whitespace-pre-wrap break-words text-slate-100">{message.content}</div>
        {message.meta ? <MessageMeta meta={message.meta} /> : null}
      </div>
    </article>
  );
}

function MessageMeta({ meta }: { meta: ChatResponse }) {
  return (
    <div className="mt-4 space-y-3 border-t border-line pt-3 text-xs text-slate-400">
      <div className="grid gap-2 md:grid-cols-3">
        <InfoPill label="Confidence" value={meta.confidence != null ? `${Math.round(meta.confidence * 100)}%` : "N/A"} />
        <InfoPill label="Grounding" value={meta.grounding_score != null ? `${Math.round(meta.grounding_score * 100)}%` : "N/A"} />
        <InfoPill label="Token" value={meta.token_estimate != null ? String(meta.token_estimate) : "N/A"} />
      </div>
      <VerificationMeta meta={meta} />
      <RouteMeta route={meta.route} />
      {meta.updated_files.length ? <CompactList title="Shard mới" items={meta.updated_files} /> : null}
      <CompactList title="Tệp liên quan" items={meta.related_files} />
      <CompactList title="Nguồn" items={meta.sources} />
    </div>
  );
}

function VerificationMeta({ meta }: { meta: ChatResponse }) {
  const verified = Boolean(meta.verification?.verified);
  const finalAction = meta.verification?.final_action ? String(meta.verification.final_action) : "answer";
  const planType = meta.plan?.task_type ? String(meta.plan.task_type) : "qa";
  return (
    <div className="rounded border border-line bg-panel px-2 py-2">
      <div className="flex flex-wrap gap-2 text-slate-300">
        <span>Plan: {planType}</span>
        <span>Verify: {verified ? "passed" : "review"}</span>
        <span>Action: {finalAction}</span>
      </div>
    </div>
  );
}

function RouteMeta({ route }: { route?: Record<string, unknown> }) {
  if (!route || !route.primary_folder) return null;
  const routes = Array.isArray(route.top_routes) ? (route.top_routes as Array<Record<string, unknown>>) : [];
  return (
    <div>
      <div className="mb-1 font-medium text-slate-300">Route tri thức</div>
      <div className="rounded border border-line bg-panel px-2 py-2">
        <div className="truncate text-slate-200">
          {String(route.primary_folder)} · {Math.round(Number(route.confidence ?? 0) * 100)}%
        </div>
        {routes.length ? (
          <div className="mt-2 space-y-1">
            {routes.slice(0, 3).map((item, index) => (
              <div key={index} className="truncate text-slate-500">
                {String(item.folder_path ?? "")} ({Math.round(Number(item.confidence ?? 0) * 100)}%)
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded border border-line bg-panel px-2 py-1">
      <span className="text-slate-500">{label}: </span>
      <span className="break-words text-slate-200">{value}</span>
    </div>
  );
}

function CompactList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <div className="mb-1 font-medium text-slate-300">{title}</div>
      <div className="max-h-24 space-y-1 overflow-auto pr-1 scrollbar-thin">
        {items.slice(0, 10).map((item, index) => (
          <div key={`${item}-${index}`} className="truncate rounded border border-line bg-panel px-2 py-1 text-slate-400">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function ThinkingBubble() {
  return (
    <article className="flex justify-start">
      <div className="w-full max-w-[760px] rounded border border-signal/30 bg-signal/10 p-4 text-sm text-slate-200">
        <div className="flex items-center gap-2">
          <Loader2 size={16} className="animate-spin text-signal" aria-hidden="true" />
          Đang điều phối agent...
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {thinkingRoles.slice(0, 4).map((role) => (
            <div key={role.stage} className="rounded border border-line bg-ink px-3 py-2 text-xs">
              <div className="flex items-center gap-2 font-semibold text-white">
                <role.icon size={14} className="text-signal" aria-hidden="true" />
                {role.name}
              </div>
              <p className="mt-1 line-clamp-2 text-slate-400">{role.description}</p>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}

function AgentThinkingPanel({ loading, meta }: { loading: boolean; meta: ChatResponse | null }) {
  const roles = meta?.agent_roles?.length ? meta.agent_roles : thinkingRoles.map(({ stage, name, description }) => ({ stage, name, description }));
  const logs = meta?.agent_logs ?? [];
  return (
    <section className="rounded border border-line bg-panel p-4 shadow-soft">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-white">Agent activity</h2>
          <p className="mt-1 text-xs text-slate-400">{loading ? `${thinkingRoles.length} agent đang hoạt động` : `${roles.length} role trong lượt gần nhất`}</p>
        </div>
        {loading ? <Loader2 size={18} className="animate-spin text-signal" aria-hidden="true" /> : <Activity size={18} className="text-accent" aria-hidden="true" />}
      </div>

      <div className="mt-4 space-y-2">
        {roles.slice(0, 8).map((role) => (
          <div key={role.stage} className="rounded border border-line bg-ink p-3">
            <div className="flex items-center justify-between gap-2">
              <div className="truncate text-xs font-semibold text-white">{role.name}</div>
              <span className="rounded bg-panel px-2 py-0.5 text-[11px] text-slate-500">{role.stage}</span>
            </div>
            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{role.description}</p>
          </div>
        ))}
      </div>

      {logs.length ? (
        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <Clock3 size={13} aria-hidden="true" />
            Timeline
          </div>
          <div className="max-h-[360px] space-y-2 overflow-auto pr-1 scrollbar-thin">
            {logs.map((log, index) => (
              <AgentLogRow key={`${log.agent}-${index}`} log={log} />
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function AgentLogRow({ log }: { log: AgentLog }) {
  const retrieval = Array.isArray(log.data?.retrieval) ? (log.data.retrieval as Array<Record<string, unknown>>) : [];
  const topRoutes = Array.isArray(log.data?.top_routes) ? (log.data.top_routes as Array<Record<string, unknown>>) : [];
  return (
    <div className="rounded border border-line bg-ink p-3 text-xs">
      <div className="grid grid-cols-[minmax(0,1fr)_44px] items-center gap-2">
        <div className="min-w-0">
          <div className="truncate font-semibold text-white">{log.agent}</div>
          <p className="mt-1 line-clamp-2 leading-5 text-slate-400">{log.message}</p>
        </div>
        <div className="text-right font-semibold text-accent">{log.score != null ? `${Math.round(log.score * 100)}%` : "..."}</div>
      </div>
      <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-slate-500">
        {log.stage ? <span>{log.stage}</span> : null}
        {log.input_count != null ? <span>in {log.input_count}</span> : null}
        {log.output_count != null ? <span>out {log.output_count}</span> : null}
        {log.runtime_ms != null ? <span>{formatRuntime(log.runtime_ms)}</span> : null}
      </div>
      {retrieval.length ? (
        <div className="mt-2 space-y-1">
          {retrieval.slice(0, 2).map((item, index) => (
            <div key={index} className="truncate rounded border border-line bg-panel px-2 py-1 text-[11px] text-slate-400">
              {String(item.file_path ?? item.preview ?? "retrieval")}
            </div>
          ))}
        </div>
      ) : null}
      {topRoutes.length ? (
        <div className="mt-2 space-y-1">
          {topRoutes.slice(0, 3).map((item, index) => (
            <div key={index} className="truncate rounded border border-line bg-panel px-2 py-1 text-[11px] text-slate-400">
              {String(item.folder_path ?? "route")} · {Math.round(Number(item.confidence ?? 0) * 100)}%
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function CleanupResultPanel({ result }: { result: KnowledgeCleanupResponse }) {
  return (
    <div className="mt-4 space-y-3 border-t border-line pt-4 text-xs">
      <div className="grid grid-cols-3 gap-2">
        <MiniStat label="Scan" value={String(result.scanned_files)} />
        <MiniStat label="Trùng" value={String(result.duplicate_groups)} />
        <MiniStat label="Nhiễu" value={String(result.noise_files)} />
      </div>
      <InfoPill label="Report" value={result.report_file} />
      <InfoPill label="Map" value={result.map_file} />
      <CompactList title="Quarantine" items={result.quarantined_files} />
      <div className="max-h-44 space-y-2 overflow-auto pr-1 scrollbar-thin">
        {result.agent_logs.map((log, index) => (
          <AgentLogRow key={`${log.agent}-${index}`} log={log} />
        ))}
      </div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-ink px-2 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

function formatRuntime(value: number) {
  if (value < 1000) return `${value}ms`;
  return `${(value / 1000).toFixed(1)}s`;
}
