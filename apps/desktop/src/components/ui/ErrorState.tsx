import { AlertTriangle } from 'lucide-react';

import { Button } from '@/components/ui/Button';

export function ErrorState({ title, message, onRetry }: { title: string; message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-ui border border-red-500/30 bg-red-500/10 p-4 text-red-100">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <AlertTriangle className="h-4 w-4" />
        {title}
      </div>
      <p className="mt-2 text-sm text-red-100/75">{message}</p>
      {onRetry ? (
        <Button className="mt-3" variant="danger" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
