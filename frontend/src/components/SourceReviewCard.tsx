import { formatValueLabel } from "../utils/labels";

interface SourceReviewCardProps {
  title: string;
  url: string;
  trust?: string;
}

export function SourceReviewCard({ title, url, trust = "unknown" }: SourceReviewCardProps) {
  return (
    <div className="rounded border border-line bg-panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-white">{title || url}</div>
          <a className="mt-1 block truncate text-xs text-signal hover:text-white" href={url} target="_blank" rel="noreferrer">
            {url}
          </a>
        </div>
        <span className="rounded border border-line px-2 py-1 text-xs text-slate-300">{formatValueLabel(trust)}</span>
      </div>
    </div>
  );
}
