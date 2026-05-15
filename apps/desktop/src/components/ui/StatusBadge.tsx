import { Badge } from '@/components/ui/Badge';
import { cn } from '@/utils/cn';

export function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const className = normalized.includes('fail')
    ? 'border-red-500/50 bg-red-500/10 text-red-200'
    : normalized.includes('running')
      ? 'border-sky-500/50 bg-sky-500/10 text-sky-200'
      : normalized.includes('approval')
        ? 'border-amber-500/50 bg-amber-500/10 text-amber-200'
        : normalized.includes('completed') || normalized.includes('success')
          ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-200'
          : 'border-line bg-panel2 text-muted';

  return <Badge className={cn('capitalize', className)}>{status.replace(/_/g, ' ')}</Badge>;
}
