// User types
export interface User {
  id: number
  username: string
  email: string
  created_at?: string
}

// Auth types
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  password_confirm: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T
  message?: string
  code?: number
}

// Learning types
export interface LearningTask {
  id: number
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  topic: string
  status: 'pending' | 'in_progress' | 'completed'
}

export interface ReviewItem {
  id: number
  topic: string
  last_reviewed: string
  ease_score: number
  due_date: string
}

// Dashboard types
export interface DashboardStats {
  today_tasks: number
  completed_tasks: number
  review_count: number
  streak_days: number
}
