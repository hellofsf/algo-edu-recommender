import type { ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import LoginPage from '@/pages/Login'
import RegisterPage from '@/pages/Register'
import DashboardPage from '@/pages/Dashboard'
import KnowledgeGraphPage from '@/pages/KnowledgeGraphPage'
import LearningPathPage from '@/pages/LearningPathPage'
import ReviewCenterPage from '@/pages/ReviewCenterPage'
import RecommendPage from '@/pages/RecommendPage'
import SettingsPage from '@/pages/SettingsPage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/graph"
          element={
            <ProtectedRoute>
              <KnowledgeGraphPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/path"
          element={
            <ProtectedRoute>
              <LearningPathPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/review"
          element={
            <ProtectedRoute>
              <ReviewCenterPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommend"
          element={
            <ProtectedRoute>
              <RecommendPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
