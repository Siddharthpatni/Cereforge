import React, { Suspense, useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { useAuthStore } from "./stores/authStore";
import apiClient from "./api/client";

// Lazy loading for performance code splitting
const Auth = React.lazy(() =>
  import("./pages/Auth").then((m) => ({ default: m.Auth })),
);
const Dashboard = React.lazy(() =>
  import("./pages/Dashboard").then((m) => ({ default: m.Dashboard })),
);
const Tasks = React.lazy(() =>
  import("./pages/Tasks").then((m) => ({ default: m.Tasks })),
);
const TaskDetail = React.lazy(() =>
  import("./pages/TaskDetail").then((m) => ({ default: m.TaskDetail })),
);
const Community = React.lazy(() =>
  import("./pages/Community").then((m) => ({ default: m.Community })),
);
const PostDetail = React.lazy(() =>
  import("./pages/PostDetail").then((m) => ({ default: m.PostDetail })),
);
const Paths = React.lazy(() =>
  import("./pages/Paths").then((m) => ({ default: m.Paths })),
);
const PathDetail = React.lazy(() =>
  import("./pages/PathDetail").then((m) => ({ default: m.PathDetail })),
);
const Leaderboard = React.lazy(() =>
  import("./pages/Leaderboard").then((m) => ({ default: m.Leaderboard })),
);
const Profile = React.lazy(() =>
  import("./pages/Profile").then((m) => ({ default: m.Profile })),
);

import PageSkeleton from "./components/ui/PageSkeleton";

function App() {
  const { isInitializing, init } = useAuthStore();

  // On mount, sync fresh user state
  useEffect(() => {
    init();
  }, [init]);

  if (isInitializing) {
    return <PageSkeleton />;
  }

  return (
    <BrowserRouter>
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          <Route
            path="/auth"
            element={
              useAuthStore.getState().isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <Auth />
              )
            }
          />

          {/* Authenticated Routes wrapped in Layout */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="tasks/:slug" element={<TaskDetail />} />
            <Route path="community" element={<Community />} />
            <Route path="community/:postId" element={<PostDetail />} />
            <Route path="leaderboard" element={<Leaderboard />} />
            <Route path="paths" element={<Paths />} />
            <Route path="paths/:slug" element={<PathDetail />} />
            <Route path="profile" element={<Profile />} />
          </Route>

          {/* Catch-all unknown routes */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
