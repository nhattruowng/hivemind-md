import { createContext, ReactNode, useContext, useMemo, useState } from "react";
import type { AgentLog } from "../api/client";

interface AgentRunState {
  logs: AgentLog[];
  latestFile: string;
  setRun: (logs: AgentLog[], latestFile: string) => void;
}

const AgentRunContext = createContext<AgentRunState | undefined>(undefined);

export function AgentRunProvider({ children }: { children: ReactNode }) {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [latestFile, setLatestFile] = useState("");

  const value = useMemo(
    () => ({
      logs,
      latestFile,
      setRun: (nextLogs: AgentLog[], file: string) => {
        setLogs(nextLogs);
        setLatestFile(file);
      }
    }),
    [logs, latestFile]
  );

  return <AgentRunContext.Provider value={value}>{children}</AgentRunContext.Provider>;
}

export function useAgentRun() {
  const value = useContext(AgentRunContext);
  if (!value) {
    throw new Error("useAgentRun must be used inside AgentRunProvider");
  }
  return value;
}

