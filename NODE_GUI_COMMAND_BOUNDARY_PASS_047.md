# Node / GUI Command Boundary — Pass 047

Node/Vite remains GUI/proxy only.

It may:

- serve the GUI;
- proxy `/api/runtime/*` to FastAPI;
- proxy `/ws/*` to FastAPI.

It may not:

- synthesize runtime events;
- decide command admissibility;
- mutate runtime truth;
- bypass FastAPI command authority.

All GUI command requests must enter through FastAPI's command authority loop.
