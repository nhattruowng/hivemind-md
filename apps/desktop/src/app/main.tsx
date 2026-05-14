import '@xyflow/react/dist/style.css';
import '@/styles/globals.css';

import { QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Toaster } from 'sonner';

import { App } from '@/app/App';
import { queryClient } from '@/app/queryClient';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster theme="dark" richColors position="bottom-right" />
    </QueryClientProvider>
  </React.StrictMode>
);
