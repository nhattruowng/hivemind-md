import { Save } from "lucide-react";
import { ChangeEvent, useEffect, useState } from "react";

const defaults = {
  ollamaBaseUrl: "http://localhost:11434",
  mainModel: "qwen2.5:7b",
  lightModel: "qwen2.5:3b",
  embedModel: "nomic-embed-text",
  maxSources: "5",
  chunkSize: "800"
};

export function Settings() {
  const [form, setForm] = useState(defaults);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem("hivemind-md-settings");
    if (raw) {
      setForm({ ...defaults, ...JSON.parse(raw) });
    }
  }, []);

  const change = (event: ChangeEvent<HTMLInputElement>) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    setSaved(false);
  };

  const save = () => {
    localStorage.setItem("hivemind-md-settings", JSON.stringify(form));
    setSaved(true);
  };

  const fields = [
    ["ollamaBaseUrl", "URL gốc của Ollama"],
    ["mainModel", "Mô hình chính"],
    ["lightModel", "Mô hình nhẹ"],
    ["embedModel", "Mô hình nhúng"],
    ["maxSources", "Số nguồn tối đa"],
    ["chunkSize", "Kích thước đoạn"]
  ] as const;

  return (
    <div className="max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Cài đặt</h1>
        <p className="mt-1 text-sm text-slate-400">Tùy chọn giao diện cục bộ cho HiveMind MD</p>
      </header>

      <section className="rounded border border-line bg-panel p-5 shadow-soft">
        <div className="grid gap-4 sm:grid-cols-2">
          {fields.map(([name, label]) => (
            <label key={name} className="block">
              <span className="text-sm font-medium text-slate-200">{label}</span>
              <input
                className="mt-2 min-h-11 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                name={name}
                value={form[name]}
                onChange={change}
              />
            </label>
          ))}
        </div>

        <div className="mt-5 flex items-center gap-3">
          <button
            className="inline-flex min-h-11 items-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink"
            onClick={save}
            type="button"
          >
            <Save size={18} aria-hidden="true" />
            Lưu
          </button>
          {saved ? <span className="text-sm text-accent">Đã lưu cục bộ</span> : null}
        </div>
      </section>
    </div>
  );
}
