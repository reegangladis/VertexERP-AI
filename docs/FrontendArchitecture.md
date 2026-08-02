# Frontend Architecture Guide - VertexERP AI

This guide details the frontend React application design implemented in **Sprint 1.3 (Enterprise Foundation Completion)**.

---

## 🏗️ Directory Map

The frontend structure under `apps/web/src` decouples presentation elements, layout containers, custom states, and endpoint routers:

```
src/
├── assets/         # Logotypes, SVG icons, and static assets
├── components/     # Reusable UI elements (Button, Card, Alert, etc.)
├── hooks/          # Global hooks pointing to Context stores
├── layouts/        # Layout boundaries (Root, Dashboard, App, Auth)
├── pages/          # Complete page components (Landing, Placeholder)
├── routes/         # Static fallback pages (NotFound, ServerError, etc.)
├── services/       # Axios API client wrapper and endpoints
├── store/          # Context providers for global state
├── styles/         # CSS variables and tailwind imports
└── tests/          # Vitest and React Testing Library setup
```

---

## 🎨 Reusable Design System

The platform styles are managed via HSL color variables in [variables.css](file:///c:/Users/ramal/Desktop/VertexERP%20AI/apps/web/src/styles/variables.css) imported by [index.css](file:///c:/Users/ramal/Desktop/VertexERP%20AI/apps/web/src/styles/index.css).

- **Colors**: tailormade colors for Light/Dark themes supporting HSL-opacity classes.
- **Spacings**: custom variables (`--spacing-xs` to `--spacing-xxl`) matching standard margins.
- **Radii**: modular corners (`--radius-sm` to `--radius-xl`).
- **Elevations**: shadow tokens (`--shadow-sm` to `--shadow-lg`).

---

## 🔄 Global State Stores

Instead of bloated external libraries, Phase 1 completes state architecture using lightweight, type-safe React Context Providers in the `src/store/` directory:

1. **`ThemeContext`**: Watches theme switches, syncs with local storage, and applies the `.dark` class to `document.documentElement`.
2. **`UIContext`**: Tracks structural UI visibility (sidebar toggle states, modal queues, active tabs).
3. **`NotificationContext`**: Handles global toast alert queues, supporting success/info/warning/error states with custom auto-dismiss timeouts.
4. **`SettingsContext`**: Holds variables (like `VITE_API_URL` and `appVersion`) and feature flags.

---

## 📡 API Client Wrapper (Axios)

API calls are coordinated in [apiClient.ts](file:///c:/Users/ramal/Desktop/VertexERP%20AI/apps/web/src/services/apiClient.ts) using `axios`:

- **Tracing Headers**: Automatically inserts unique `X-Request-ID` tracers into all outgoing headers.
- **Response Handler**: Unwraps backend envelopes, throwing friendly error details if `success` is false.
- **Resilient Fallback**: Parses service states even on HTTP 503 error payloads.

---

## 🖥️ Layout & Routing Matrix

The routing architecture in [App.tsx](file:///c:/Users/ramal/Desktop/VertexERP%20AI/apps/web/src/App.tsx) uses nested route layouts:

- **`AppLayout`**: Handles toast notifications.
- **`DashboardLayout`**: Wraps dashboard views with the collapsible Sidebar and top Header.
- **`AuthLayout`**: Centers authentication views (placeholder for Phase 2).
- **`ErrorBoundary`**: Intercepts rendering exceptions and renders `ErrorLayout`.
