import { Clipboard, RefreshCw, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { deleteKnowledge, listKnowledge, readKnowledge, type KnowledgeItem } from "../api/client";
import { MarkdownPreview } from "../components/MarkdownPreview";

export function KnowledgeExplorer() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [category, setCategory] = useState("all");
  const [selected, setSelected] = useState<KnowledgeItem | null>(null);
  const [content, setContent] = useState("");
  const [notice, setNotice] = useState("");

  const refresh = async () => {
    const data = await listKnowledge();
    setItems(data);
    if (data.length && !selected) {
      setSelected(data[0]);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  useEffect(() => {
    if (!selected) {
      setContent("");
      return;
    }
    void readKnowledge(selected.file_path).then((data) => setContent(data.content));
  }, [selected]);

  const categories = useMemo(() => ["all", ...Array.from(new Set(items.map((item) => item.category)))], [items]);
  const filtered = category === "all" ? items : items.filter((item) => item.category === category);

  const remove = async () => {
    if (!selected) return;
    const approved = window.confirm(`Xóa tệp knowledge này?\n\n${selected.file_path}`);
    if (!approved) return;
    await deleteKnowledge(selected.file_path, true);
    setNotice(`Đã xóa ${selected.file_path}`);
    setSelected(null);
    setContent("");
    await refresh();
  };

  const copy = async () => {
    if (!content) return;
    await navigator.clipboard.writeText(content);
    setNotice("Đã sao chép Markdown");
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
      <section className="space-y-4">
        <header>
          <h1 className="text-2xl font-semibold text-white">Khám phá tri thức</h1>
          <p className="mt-1 text-sm text-slate-400">Duyệt các tệp Markdown đã lưu</p>
        </header>

        <div className="rounded border border-line bg-panel p-4">
          <div className="flex gap-2">
            <select
              className="min-h-10 flex-1 rounded border border-line bg-ink px-3 text-sm text-white"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              {categories.map((item) => (
                <option key={item} value={item}>
                  {item === "all" ? "Tất cả" : item}
                </option>
              ))}
            </select>
            <button className="grid h-10 w-10 place-items-center rounded border border-line text-slate-200 hover:bg-white/10" onClick={() => void refresh()} title="Làm mới">
              <RefreshCw size={17} aria-hidden="true" />
            </button>
          </div>
        </div>

        <div className="max-h-[58vh] space-y-2 overflow-auto scrollbar-thin">
          {filtered.map((item) => (
            <button
              key={item.file_path}
              className={[
                "w-full rounded border p-4 text-left transition",
                selected?.file_path === item.file_path ? "border-signal bg-signal/10" : "border-line bg-panel hover:bg-white/5"
              ].join(" ")}
              onClick={() => setSelected(item)}
            >
              <div className="truncate text-sm font-semibold text-white">{item.title}</div>
              <div className="mt-2 flex items-center justify-between gap-3 text-xs text-slate-400">
                <span>{item.category}</span>
                <span>{item.trust_score?.toFixed(2) ?? "không có"}</span>
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="min-w-0 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate text-sm text-slate-400">{selected?.file_path ?? "Chưa chọn tệp"}</p>
            {notice ? <p className="mt-1 text-xs text-accent">{notice}</p> : null}
          </div>
          <div className="flex gap-2">
            <button
              className="inline-flex min-h-10 items-center gap-2 rounded border border-line px-3 text-sm text-slate-200 hover:bg-white/10 disabled:opacity-40"
              disabled={!content}
              onClick={() => void copy()}
            >
              <Clipboard size={16} aria-hidden="true" />
              Sao chép
            </button>
            <button
              className="inline-flex min-h-10 items-center gap-2 rounded border border-red-400/40 px-3 text-sm text-red-200 hover:bg-red-400/10 disabled:opacity-40"
              disabled={!selected}
              onClick={() => void remove()}
            >
              <Trash2 size={16} aria-hidden="true" />
              Xóa
            </button>
          </div>
        </div>
        <MarkdownPreview content={content} />
      </section>
    </div>
  );
}
