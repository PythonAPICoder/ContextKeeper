# ContextKeeper Architecture

    Clients
    (AnythingLLM, Open WebUI, IDEs, Python)
                  │
                  ▼
          ContextKeeper Proxy
                  │
       ┌──────────┼──────────┐
       │          │          │
    Context   Diagnostics   Routing
     Engine      Engine      Engine
                  │
                  ▼
                Ollama
                  │
                  ▼
                 Models

## Initial Modules

-   proxy/
-   context/
-   diagnostics/
-   dashboard/
-   routing/
-   memory/
-   plugins/
-   utils/

The proxy remains the only component visible to clients.
