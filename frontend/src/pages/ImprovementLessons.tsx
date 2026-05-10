import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { archiveLesson, listImprovementLessons, type ImprovementLesson } from "../api/client";
import { LessonCard } from "../components/self-improvement/LessonCard";

export function ImprovementLessons() {
  const [lessons, setLessons] = useState<ImprovementLesson[]>([]);
  const [agentName, setAgentName] = useState("");
  const [lessonType, setLessonType] = useState("");
  const [status, setStatus] = useState("active");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setLessons(
        await listImprovementLessons({
          agent_name: agentName || undefined,
          lesson_type: lessonType || undefined,
          status: status || undefined
        })
      );
    } finally {
      setLoading(false);
    }
  };

  const archive = async (id: number) => {
    await archiveLesson(id);
    await load();
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Bài học cải thiện</h1>
        <p className="mt-1 text-sm text-slate-400">Bài học có thể tái sử dụng được lưu trong SQLite và bộ nhớ Markdown</p>
      </header>

      <section className="grid gap-3 rounded border border-line bg-panel p-4 shadow-soft lg:grid-cols-[1fr_160px_160px_auto]">
        <input
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setAgentName(event.target.value)}
          placeholder="Tên tác nhân"
          value={agentName}
        />
        <select
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setLessonType(event.target.value)}
          value={lessonType}
        >
          <option value="">Tất cả loại</option>
          <option value="prompt">Lời nhắc</option>
          <option value="workflow">Quy trình</option>
          <option value="tool">Công cụ</option>
          <option value="error">Lỗi</option>
          <option value="success">Thành công</option>
          <option value="failed">Thất bại</option>
        </select>
        <select
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setStatus(event.target.value)}
          value={status}
        >
          <option value="">Tất cả trạng thái</option>
          <option value="active">Đang dùng</option>
          <option value="archived">Đã lưu trữ</option>
        </select>
        <button
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:opacity-60"
          disabled={loading}
          onClick={() => void load()}
          type="button"
        >
          <RefreshCcw size={16} aria-hidden="true" />
          Làm mới
        </button>
      </section>

      <section className="space-y-4">
        {lessons.map((lesson) => (
          <LessonCard key={lesson.id} lesson={lesson} onArchive={(id) => void archive(id)} />
        ))}
        {!lessons.length ? <p className="rounded border border-line bg-panel p-5 text-sm text-slate-400">Chưa có bài học.</p> : null}
      </section>
    </div>
  );
}
