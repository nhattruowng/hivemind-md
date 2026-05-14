import type { ReactNode } from 'react';

import { cn } from '@/utils/cn';

interface BadgeProps {
  children: ReactNode;
  className?: string;
}

export function Badge({ children, className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center rounded border border-line bg-panel2 px-2 py-0.5 text-xs text-muted', className)}>
      {children}
    </span>
  );
}
