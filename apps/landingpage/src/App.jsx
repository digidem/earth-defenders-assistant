import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { navItems } from "./nav-items";

const queryClient = new QueryClient();

const baseUrl = import.meta.env.BASE_URL || "/";

const router = createBrowserRouter(
  navItems.map(({ to, page }) => ({
    path: to,
    element: page,
  })),
  { basename: baseUrl },
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <RouterProvider router={router} />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
