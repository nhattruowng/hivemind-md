import { Activity, Boxes, Clock3, Database, Server } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { healthCheck, listKnowledge, ollamaHealth, type KnowledgeItem } from "../api/client";
import { formatValueLabel } from "../utils/labels";

export function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [ollamaStatus, setOllamaStatus] = useState("checking");
  const [items, setItems] = useState<KnowledgeItem[]>([]);

  useEffect(() => {
    void Promise.all([
      healthCheck().then((data) => setBackendStatus(data.status)).catch(() => setBackendStatus("offline")),
      ollamaHealth().then((data) => setOllamaStatus(data.status)).catch(() => setOllamaStatus("offline")),
      listKnowledge().then(setItems).catch(() => setItems([]))
    ]);
  }, []);

  const categories = useMemo(() => new Set(items.map((item) => item.category)).size, [items]);
  const latest = items[0]?.updated_at ? new Date(items[0].updated_at).toLocaleString("vi-VN") : "Chưa có cập nhật";

  const cards = [
    { label: "Tệp tri thức", value: items.length, icon: Database },
    { label: "Danh mục", value: categories, icon: Boxes },
    { label: "Máy chủ", value: formatValueLabel(backendStatus), icon: Server },
    { label: "Ollama", value: formatValueLabel(ollamaStatus), icon: Activity }
  ];

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-white">Bảng điều khiển</h1>
        <p className="text-sm text-slate-400">Tổng quan trạng thái vận hành HiveMind MD</p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="rounded border border-line bg-panel p-5 shadow-soft">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-400">{card.label}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
                </div>
                <div className="grid h-11 w-11 place-items-center rounded bg-white/10 text-signal">
                  <Icon size={21} aria-hidden="true" />
                </div>
              </div>
            </div>
          );
        })}
      </section>

      <section className="rounded border border-line bg-panel p-5">
        <div className="flex items-center gap-3">
          <Clock3 className="text-accent" size={20} aria-hidden="true" />
          <div>
            <p className="text-sm text-slate-400">Cập nhật gần nhất</p>
            <p className="text-base font-medium text-white">{latest}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
