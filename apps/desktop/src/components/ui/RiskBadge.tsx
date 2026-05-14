import { Badge } from '@/components/ui/Badge';
import type { RiskLevel } from '@/types/common.types';
import { cn } from '@/utils/cn';

const riskClasses: Record<RiskLevel, string> = {
  low: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
  medium: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
  high: 'border-red-500/50 bg-red-500/10 text-red-200',
  critical: 'border-rose-400/70 bg-rose-500/20 text-rose-100'
};

export function RiskBadge({ risk }: { risk: RiskLevel }) {
  return <Badge className={cn('capitalize', riskClasses[risk])}>Risk: {risk}</Badge>;
}
