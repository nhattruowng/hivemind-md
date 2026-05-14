import { AppShell } from '@/components/layout/AppShell';
import { WorkflowBuilderPage } from '@/features/workflows/pages/WorkflowBuilderPage';

export function App() {
  return (
    <AppShell>
      <WorkflowBuilderPage />
    </AppShell>
  );
}
