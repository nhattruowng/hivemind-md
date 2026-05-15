import { AppShell } from '@/components/layout/AppShell';
import { ApprovalInboxPage } from '@/features/approvals/pages/ApprovalInboxPage';
import { AgentStudioPage } from '@/features/agent-studio/pages/AgentStudioPage';
import { WorkflowBuilderPage } from '@/features/workflows/pages/WorkflowBuilderPage';
import { useUiStore } from '@/stores/ui.store';
import type { ReactNode } from 'react';
import {
  AlertTriangle,
  Bot,
  Brain,
  CheckCircle2,
  Database,
  FileSearch,
  GitBranch,
  KeyRound,
  Lock,
  Play,
  Search,
  ShieldAlert,
  Terminal,
  Wrench,
  type LucideIcon
} from 'lucide-react';

export function App() {
  const activePage = useUiStore((state) => state.activePage);

  return (
    <AppShell>
      {activePage === 'dashboard' && <DashboardPage />}
      {activePage === 'workflows' && <WorkflowBuilderPage />}
      {activePage === 'approvals' && <ApprovalInboxPage />}
      {activePage === 'agent-studio' && <AgentStudioPage />}
      {activePage === 'chat' && <WorkspacePage kind="chat" />}
      {activePage === 'memory' && <WorkspacePage kind="memory" />}
      {activePage === 'tools' && <WorkspacePage kind="tools" />}
      {activePage === 'permissions' && <WorkspacePage kind="permissions" />}
      {activePage === 'models' && <WorkspacePage kind="models" />}
      {activePage === 'connectors' && <WorkspacePage kind="connectors" />}
      {activePage === 'audit' && <WorkspacePage kind="audit" />}
      {activePage === 'settings' && <WorkspacePage kind="settings" />}
    </AppShell>
  );
}

function DashboardPage() {
  return (
    <div className="h-full overflow-y-auto bg-canvas">
      <section className="border-b border-line bg-panel px-6 py-5">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="text-xs font-medium uppercase tracking-[0.18em] text-sky-300">BizFlow Local Agent</div>
            <h1 className="mt-2 text-2xl font-semibold text-text">Bảng điều khiển AI Agent local-first</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
              Theo dõi agent đang đọc gì, nhớ gì, gọi tool nào, workflow nào đang chạy và approval nào đang chờ duyệt.
              Dữ liệu mặc định ở local, hành động nguy hiểm luôn qua permission và approval gate.
            </p>
          </div>
          <div className="flex gap-2">
            <button className="rounded-ui border border-line bg-panel2 px-3 py-2 text-sm text-muted hover:text-text">
              Privacy: local only
            </button>
            <button className="rounded-ui bg-sky-500 px-3 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400">
              New workflow
            </button>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-4 gap-4 p-5">
        <MetricCard icon={Brain} label="Memory nodes" value="1,284" detail="98% có source trace" tone="sky" />
        <MetricCard icon={ShieldAlert} label="Pending approvals" value="3" detail="1 high risk action" tone="amber" />
        <MetricCard icon={GitBranch} label="Workflow runs" value="17" detail="2 đang chờ user" tone="emerald" />
        <MetricCard icon={Database} label="Model route" value="Local" detail="Cloud bị tắt mặc định" tone="rose" />
      </section>

      <section className="grid grid-cols-[1.1fr_0.9fr] gap-4 px-5 pb-5">
        <Panel title="Agent Activity" subtitle="Planner / Executor / Verifier trace">
          <TimelineItem icon={Bot} title="Intent Router" detail="Phân loại request: workflow automation" status="done" />
          <TimelineItem icon={Search} title="Context Builder" detail="Đã lấy 6 memory có confidence > 0.78" status="done" />
          <TimelineItem icon={Wrench} title="Tool Router" detail="write_local_file bị chặn, cần approval" status="warning" />
          <TimelineItem icon={CheckCircle2} title="Verifier" detail="Kiểm tra response, không gửi sensitive data lên cloud" status="done" />
        </Panel>

        <Panel title="Approval Inbox" subtitle="Hành động nguy hiểm đang bị giữ lại">
          <ApprovalRow risk="high" action="delete_local_file" resource="D:/client/archive/raw.pdf" />
          <ApprovalRow risk="medium" action="create_note" resource="Daily report draft" />
          <ApprovalRow risk="critical" action="run_shell_command" resource="npm audit fix --force" />
        </Panel>
      </section>

      <section className="grid grid-cols-3 gap-4 px-5 pb-6">
        <Panel title="Memory Control" subtitle="Source trace, version, confidence">
          <MiniRow icon={FileSearch} label="Source viewer" value="PDF page/line/chunk trace" />
          <MiniRow icon={Brain} label="Conflict review" value="4 contradictions pending" />
          <MiniRow icon={Lock} label="Sensitive memory" value="local_only enforced" />
        </Panel>

        <Panel title="Workflow Engine" subtitle="Retry, pause, resume, replay/debug">
          <MiniRow icon={GitBranch} label="Builder" value="Drag/drop DSL canvas" />
          <MiniRow icon={Play} label="Run timeline" value="Step input/output redacted" />
          <MiniRow icon={AlertTriangle} label="Replay policy" value="New approval for risky replay" />
        </Panel>

        <Panel title="Tool Runtime" subtitle="Permission by action/path/risk">
          <MiniRow icon={Wrench} label="Tools enabled" value="8 built-in tools" />
          <MiniRow icon={KeyRound} label="Folder scopes" value="3 allowed folders" />
          <MiniRow icon={Terminal} label="Shell" value="approval required" />
        </Panel>
      </section>
    </div>
  );
}

function WorkspacePage({ kind }: { kind: string }) {
  const content: Record<string, { title: string; subtitle: string; items: string[] }> = {
    chat: {
      title: 'Chat with Agent',
      subtitle: 'Chat panel với memory citations, tool call cards và trace drawer.',
      items: ['Conversation list', 'Memory citation cards', 'Approval needed banner', 'Planner / Executor / Verifier trace']
    },
    memory: {
      title: 'Memory Map',
      subtitle: 'Xem agent đang nhớ gì, nguồn từ đâu và confidence bao nhiêu.',
      items: ['Semantic + keyword search', 'Source trace viewer', 'Version history', 'Conflict review']
    },
    tools: {
      title: 'Tool Manager',
      subtitle: 'Quản lý tool schema, risk level, permission và test console.',
      items: ['read/write/list/search tools', 'JSON Schema validation', 'Allowed/blocked paths', 'Audit per tool call']
    },
    permissions: {
      title: 'Permission Center',
      subtitle: 'Default deny cho write/delete/shell/network/cloud sensitive.',
      items: ['Folder scopes', 'Risk rules', 'Model privacy rules', 'Tool policies']
    },
    models: {
      title: 'Model Settings',
      subtitle: 'Local model qua Ollama/llama.cpp, cloud model opt-in.',
      items: ['Ollama status', 'Cloud provider settings', 'Routing rules', 'Sensitive data policy']
    },
    connectors: {
      title: 'Connector Manager',
      subtitle: 'Local files trước, Gmail/Calendar/Drive/GitHub/Notion ở phase sau.',
      items: ['Local folder sync', 'Permission scope', 'Sync history', 'Connector errors']
    },
    audit: {
      title: 'Audit Log',
      subtitle: 'Query mọi agent run, memory read/write, tool call, approval và workflow step.',
      items: ['Filter by risk/tool/workflow', 'Redacted input/output', 'Trace JSON', 'Export logs']
    },
    settings: {
      title: 'Settings',
      subtitle: 'Privacy, storage, backup/export, theme và developer mode.',
      items: ['Local data path', 'Encrypted backup', 'Clear all memory', 'Developer mode']
    }
  };
  const page = content[kind];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">{page.title}</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted">{page.subtitle}</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {page.items.map((item) => (
          <div key={item} className="rounded-ui border border-line bg-panel p-4">
            <div className="text-sm font-medium">{item}</div>
            <p className="mt-2 text-sm leading-6 text-muted">
              Khung UI đã được đặt đúng module để nối API, state và loading/error/empty state theo yêu cầu phase desktop.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  tone
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  detail: string;
  tone: 'sky' | 'amber' | 'emerald' | 'rose';
}) {
  const tones = {
    sky: 'border-sky-500/30 bg-sky-500/10 text-sky-200',
    amber: 'border-amber-500/30 bg-amber-500/10 text-amber-200',
    emerald: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
    rose: 'border-rose-500/30 bg-rose-500/10 text-rose-200'
  };
  return (
    <div className="rounded-ui border border-line bg-panel p-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">{label}</div>
        <div className={`rounded-ui border p-2 ${tones[tone]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-muted">{detail}</div>
    </div>
  );
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <div className="rounded-ui border border-line bg-panel">
      <div className="border-b border-line px-4 py-3">
        <div className="text-sm font-semibold">{title}</div>
        <div className="mt-1 text-xs text-muted">{subtitle}</div>
      </div>
      <div className="space-y-3 p-4">{children}</div>
    </div>
  );
}

function TimelineItem({
  icon: Icon,
  title,
  detail,
  status
}: {
  icon: LucideIcon;
  title: string;
  detail: string;
  status: 'done' | 'warning';
}) {
  return (
    <div className="flex gap-3 rounded-ui border border-line bg-canvas p-3">
      <div className={status === 'done' ? 'text-emerald-300' : 'text-amber-300'}>
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <div className="text-sm font-medium">{title}</div>
        <div className="mt-1 text-xs text-muted">{detail}</div>
      </div>
    </div>
  );
}

function ApprovalRow({ risk, action, resource }: { risk: string; action: string; resource: string }) {
  return (
    <div className="rounded-ui border border-line bg-canvas p-3">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium">{action}</div>
        <span className="rounded border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 text-xs text-rose-200">{risk}</span>
      </div>
      <div className="mt-2 truncate text-xs text-muted">{resource}</div>
    </div>
  );
}

function MiniRow({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 rounded-ui border border-line bg-canvas p-3">
      <Icon className="h-4 w-4 text-sky-300" />
      <div className="min-w-0">
        <div className="text-sm font-medium">{label}</div>
        <div className="truncate text-xs text-muted">{value}</div>
      </div>
    </div>
  );
}
