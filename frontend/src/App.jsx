import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { useAuthStore } from './stores/authStore';
import apiClient from './api/client';

// Standard imports rather than lazy loading for simplicity in this build
import { Auth } from './pages/Auth';
import { Dashboard } from './pages/Dashboard';
import { Tasks } from './pages/Tasks';
import { TaskDetail } from './pages/TaskDetail';
import { Community } from './pages/Community';
import { PostDetail } from './pages/PostDetail';
import { Paths } from './pages/Paths';
import { PathDetail } from './pages/PathDetail';
import { Leaderboard } from './pages/Leaderboard';
import { Profile } from './pages/Profile';

function App() {
  const { isAuthenticated, setUser, logout } = useAuthStore();

  // On mount, sync fresh user state
  useEffect(() => {
    if (isAuthenticated) {
      apiClient.get('/auth/me')
        .then(res => setUser(res.data.user, res.data.rank))
        .catch(err => {
          console.error("Failed to fetch user data on mount", err);
          if (err.response?.status === 401) logout();
        });
    }
  }, [isAuthenticated, setUser, logout]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={isAuthenticated ? <Navigate to="/" replace /> : <Auth />} />

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
          <Route path="profile/:username" element={<Profile />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
