import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AgentMonitor } from "./pages/AgentMonitor";
import { AgentRuns } from "./pages/AgentRuns";
import { ChatWithKnowledge } from "./pages/ChatWithKnowledge";
import { Dashboard } from "./pages/Dashboard";
import { ImprovementLessons } from "./pages/ImprovementLessons";
import { KnowledgeBuilder } from "./pages/KnowledgeBuilder";
import { KnowledgeExplorer } from "./pages/KnowledgeExplorer";
import { PromptVersions } from "./pages/PromptVersions";
import { SelfImprovementDashboard } from "./pages/SelfImprovementDashboard";
import { Settings } from "./pages/Settings";
import { WorkflowSuggestions } from "./pages/WorkflowSuggestions";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="/builder" element={<KnowledgeBuilder />} />
        <Route path="/agents" element={<AgentMonitor />} />
        <Route path="/knowledge" element={<KnowledgeExplorer />} />
        <Route path="/chat" element={<ChatWithKnowledge />} />
        <Route path="/self-improvement" element={<SelfImprovementDashboard />} />
        <Route path="/self-improvement/runs" element={<AgentRuns />} />
        <Route path="/self-improvement/prompts" element={<PromptVersions />} />
        <Route path="/self-improvement/lessons" element={<ImprovementLessons />} />
        <Route path="/self-improvement/workflows" element={<WorkflowSuggestions />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
