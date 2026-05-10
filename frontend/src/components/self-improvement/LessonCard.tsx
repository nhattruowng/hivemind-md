import { Archive } from "lucide-react";
import type { ImprovementLesson } from "../../api/client";
import { ImprovementPolicyBadge } from "./ImprovementPolicyBadge";

interface LessonCardProps {
  lesson: ImprovementLesson;
  onArchive?: (id: number) => void;
}

export function LessonCard({ lesson, onArchive }: LessonCardProps) {
  return (
    <article className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="break-words text-lg font-semibold text-white">{lesson.title}</h2>
            <ImprovementPolicyBadge value={lesson.lesson_type} />
            <ImprovementPolicyBadge value={lesson.status} />
          </div>
          <p className="text-sm text-slate-400">
            {lesson.agent_name ?? "Mọi tác nhân"} · {new Date(lesson.created_at).toLocaleString("vi-VN")}
          </p>
        </div>
        {lesson.status !== "archived" && onArchive ? (
          <button
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded border border-line px-3 text-sm text-slate-200 transition hover:bg-white/10"
            onClick={() => onArchive(lesson.id)}
            type="button"
          >
            <Archive size={16} aria-hidden="true" />
            Lưu trữ
          </button>
        ) : null}
      </div>
      <pre className="mt-4 whitespace-pre-wrap break-words rounded border border-line bg-ink p-4 text-sm leading-6 text-slate-300">
        {lesson.content}
      </pre>
    </article>
  );
}
