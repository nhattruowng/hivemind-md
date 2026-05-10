import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AgentRunProvider } from "./context/AgentRunContext";
import App from "./App";
import "./styles/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AgentRunProvider>
        <App />
      </AgentRunProvider>
    </BrowserRouter>
  </React.StrictMode>
);

