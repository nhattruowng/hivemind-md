interface MarkdownPreviewProps {
  content: string;
}

export function MarkdownPreview({ content }: MarkdownPreviewProps) {
  if (!content) {
    return (
      <div className="rounded border border-dashed border-line bg-panel p-6 text-sm text-slate-400">
        Chưa chọn nội dung Markdown.
      </div>
    );
  }

  return (
    <article className="max-h-[70vh] overflow-auto rounded border border-line bg-[#0d1117] p-5 text-sm leading-7 text-slate-200 scrollbar-thin">
      {content.split("\n").map((line, index) => {
        const key = `${index}-${line.slice(0, 8)}`;
        if (line.startsWith("# ")) {
          return (
            <h1 key={key} className="mb-4 mt-1 text-2xl font-semibold text-white">
              {line.replace("# ", "")}
            </h1>
          );
        }
        if (line.startsWith("## ")) {
          return (
            <h2 key={key} className="mb-2 mt-6 border-b border-line pb-2 text-lg font-semibold text-white">
              {line.replace("## ", "")}
            </h2>
          );
        }
        if (line.startsWith("- ")) {
          return (
            <div key={key} className="flex gap-2">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-signal" />
              <p className="m-0 min-w-0 break-words">{line.replace("- ", "")}</p>
            </div>
          );
        }
        if (!line.trim()) {
          return <div key={key} className="h-3" />;
        }
        return (
          <p key={key} className="min-w-0 break-words">
            {line}
          </p>
        );
      })}
    </article>
  );
}
