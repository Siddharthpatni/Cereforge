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

// Loading Fallback Component
const PageLoader = () => (
  <div className="flex h-full min-h-[50vh] w-full items-center justify-center">
    <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-800 border-t-primary"></div>
  </div>
);

function App() {
  const { isAuthenticated, setUser, logout } = useAuthStore();

  // On mount, sync fresh user state
  useEffect(() => {
    if (isAuthenticated) {
      apiClient
        .get("/auth/me")
        .then((res) => setUser(res.data.user, res.data.rank))
        .catch((err) => {
          console.error("Failed to fetch user data on mount", err);
          if (err.response?.status === 401) logout();
        });
    }
  }, [isAuthenticated, setUser, logout]);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/auth"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Suspense fallback={<PageLoader />}>
                <Auth />
              </Suspense>
            )
          }
        />

        {/* Authenticated Routes wrapped in Layout */}
        <Route path="/" element={<Layout />}>
          <Route
            element={
              <Suspense fallback={<PageLoader />}>
                <Outlet />
              </Suspense>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="tasks/:slug" element={<TaskDetail />} />
            <Route path="community" element={<Community />} />
            <Route path="community/:postId" element={<PostDetail />} />
            <Route path="leaderboard" element={<Leaderboard />} />
            <Route path="paths" element={<Paths />} />
            <Route path="paths/:slug" element={<PathDetail />} />
            <Route path="profile" element={<Profile />} />
            <Route path="profile/:username" element={<Profile />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
