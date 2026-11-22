import React from "react";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";
import { AppProviders } from "./providers";

export const App: React.FC = () => {
  return (
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  );
};
