import type { ButtonHTMLAttributes, ReactNode } from 'react';

import { cn } from '@/utils/cn';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: ReactNode;
}

const variants: Record<ButtonVariant, string> = {
  primary: 'border-sky-500/70 bg-sky-500/15 text-sky-100 hover:bg-sky-500/25',
  secondary: 'border-line bg-panel2 text-text hover:bg-slate-700/60',
  ghost: 'border-transparent bg-transparent text-muted hover:bg-panel2 hover:text-text',
  danger: 'border-red-500/70 bg-red-500/15 text-red-100 hover:bg-red-500/25'
};

export function Button({ className, variant = 'secondary', icon, children, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex h-9 items-center justify-center gap-2 rounded-ui border px-3 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-sky-400 disabled:cursor-not-allowed disabled:opacity-50',
        variants[variant],
        className
      )}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}
