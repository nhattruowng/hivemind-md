import { cn } from '@/utils/cn';

export function LoadingSkeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-ui bg-slate-700/50', className)} />;
}
