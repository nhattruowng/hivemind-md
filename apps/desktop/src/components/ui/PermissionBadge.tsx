import { Badge } from '@/components/ui/Badge';
import type { PermissionLevel } from '@/types/common.types';

export function PermissionBadge({ permission }: { permission: PermissionLevel }) {
  return <Badge>{permission.replace(/_/g, ' ')}</Badge>;
}
