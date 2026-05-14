import {
  Bot,
  BrainCircuit,
  Database,
  Gauge,
  GitPullRequest,
  History,
  MessageSquareText,
  Network,
  PanelsTopLeft,
  NotebookText,
  Settings,
  Sparkles,
  WandSparkles
} from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Bảng điều khiển", icon: Gauge },
  { to: "/builder", label: "Tạo tri thức", icon: WandSparkles },
  { to: "/agent-studio", label: "Agent Studio", icon: PanelsTopLeft },
  { to: "/agents", label: "Giám sát tác nhân", icon: Network },
  { to: "/knowledge", label: "Khám phá tri thức", icon: Database },
  { to: "/chat", label: "Trò chuyện", icon: MessageSquareText },
  { to: "/self-improvement", label: "Tự cải thiện", icon: BrainCircuit },
  { to: "/self-improvement/runs", label: "Lượt chạy tác nhân", icon: History },
  { to: "/self-improvement/prompts", label: "Phiên bản lời nhắc", icon: Sparkles },
  { to: "/self-improvement/lessons", label: "Bài học cải thiện", icon: NotebookText },
  { to: "/self-improvement/workflows", label: "Gợi ý quy trình", icon: GitPullRequest },
  { to: "/settings", label: "Cài đặt", icon: Settings }
];

export function Sidebar() {
  return (
    <aside className="flex h-full w-full flex-col border-r border-line bg-[#11151d]">
      <div className="flex h-16 items-center gap-3 border-b border-line px-5">
        <div className="grid h-9 w-9 place-items-center rounded bg-accent text-ink">
          <Bot size={20} aria-hidden="true" />
        </div>
        <div>
          <div className="text-sm font-semibold uppercase tracking-wide text-white">HiveMind MD</div>
          <div className="text-xs text-slate-400">Tác nhân tri thức cục bộ</div>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex min-h-11 items-center gap-3 rounded px-3 text-sm transition",
                  isActive ? "bg-white text-ink" : "text-slate-300 hover:bg-white/10 hover:text-white"
                ].join(" ")
              }
            >
              <Icon size={18} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
