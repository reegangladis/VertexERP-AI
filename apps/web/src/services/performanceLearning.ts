import { apiClient } from './apiClient';

export interface Goal {
  id: string;
  organization_id: string;
  employee_id: string;
  title: string;
  description?: string;
  goal_type: string;
  priority: string;
  weightage: number;
  start_date: string;
  end_date: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
  key_results?: KeyResult[];
}

export interface KeyResult {
  id: string;
  goal_id: string;
  title: string;
  target_value: number;
  current_value: number;
  measurement_unit: string;
  progress: number;
  status: string;
}

export interface PerformanceReviewCycle {
  id: string;
  organization_id: string;
  name: string;
  review_type: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface PerformanceReview {
  id: string;
  employee_id: string;
  review_cycle_id: string;
  reviewer_id: string;
  overall_rating?: number;
  overall_score?: number;
  status: string;
  submitted_at?: string;
  feedbacks?: PerformanceFeedback[];
}

export interface PerformanceFeedback {
  id: string;
  review_id: string;
  feedback_type: string;
  comments?: string;
  rating?: number;
  submitted_by: string;
  submitted_at?: string;
}

export interface Competency {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  category: string;
}

export interface EmployeeCompetency {
  id: string;
  employee_id: string;
  competency_id: string;
  rating: number;
  verified: boolean;
}

export interface TrainingCourse {
  id: string;
  organization_id: string;
  course_name: string;
  course_code: string;
  description?: string;
  duration_hours: number;
  difficulty: string;
  category: string;
  status: string;
}

export interface CourseEnrollment {
  id: string;
  employee_id: string;
  course_id: string;
  enrolled_at: string;
  completed_at?: string;
  completion_percentage: number;
  status: string;
}

export interface TrainingProgram {
  id: string;
  organization_id: string;
  program_name: string;
  description?: string;
  status: string;
}

export interface LearningCertificate {
  id: string;
  employee_id: string;
  course_id: string;
  certificate_number: string;
  issue_date: string;
  expiry_date?: string;
  certificate_url?: string;
}

export interface SkillMatrix {
  id: string;
  employee_id: string;
  skill_name: string;
  category: string;
  current_level: string;
  target_level: string;
  last_updated: string;
}

export interface PerformanceDashboardData {
  total_goals: number;
  completed_goals: number;
  average_goal_progress: number;
  active_review_cycles: number;
  pending_reviews: number;
  average_performance_rating: number;
  promotion_readiness_score: number;
  performance_trends: Array<{ period: string; rating: number; goalCompletion: number }>;
}

export interface TrainingDashboardData {
  total_courses: number;
  active_enrollments: number;
  completed_courses: number;
  total_certificates: number;
  avg_learning_progress: number;
  skills_tracked: number;
  skill_gap_percentage: number;
}

export const performanceLearningService = {
  // Goals
  getGoals: async (employeeId: string) => {
    const res = await apiClient.get<Goal[]>(`/api/v1/goals?employee_id=${employeeId}`);
    return res.data;
  },
  createGoal: async (data: Partial<Goal>) => {
    const res = await apiClient.post<Goal>('/api/v1/goals', data);
    return res.data;
  },
  updateGoal: async (id: string, data: Partial<Goal>) => {
    const res = await apiClient.put<Goal>(`/api/v1/goals/${id}`, data);
    return res.data;
  },
  deleteGoal: async (id: string) => {
    await apiClient.delete(`/api/v1/goals/${id}`);
  },

  // Key Results
  addKeyResult: async (goalId: string, data: Partial<KeyResult>) => {
    const res = await apiClient.post<KeyResult>(`/api/v1/goals/${goalId}/key-results`, data);
    return res.data;
  },
  updateKeyResult: async (krId: string, data: Partial<KeyResult>) => {
    const res = await apiClient.put<KeyResult>(`/api/v1/key-results/${krId}`, data);
    return res.data;
  },

  // Performance Reviews & Cycles
  getReviewCycles: async (orgId: string) => {
    const res = await apiClient.get<PerformanceReviewCycle[]>(`/api/v1/review-cycles?org_id=${orgId}`);
    return res.data;
  },
  createReviewCycle: async (data: Partial<PerformanceReviewCycle>) => {
    const res = await apiClient.post<PerformanceReviewCycle>('/api/v1/review-cycles', data);
    return res.data;
  },
  getReviews: async (employeeId: string) => {
    const res = await apiClient.get<PerformanceReview[]>(`/api/v1/reviews?employee_id=${employeeId}`);
    return res.data;
  },
  createReview: async (data: Partial<PerformanceReview>) => {
    const res = await apiClient.post<PerformanceReview>('/api/v1/reviews', data);
    return res.data;
  },
  submitReview: async (reviewId: string) => {
    const res = await apiClient.post<PerformanceReview>(`/api/v1/reviews/${reviewId}/submit`);
    return res.data;
  },

  // Feedback (Self, Manager, Peer, 360)
  submitFeedback: async (data: Partial<PerformanceFeedback>) => {
    const res = await apiClient.post<PerformanceFeedback>('/api/v1/feedback', data);
    return res.data;
  },
  getFeedbackForReview: async (reviewId: string) => {
    const res = await apiClient.get<PerformanceFeedback[]>(`/api/v1/feedback/review/${reviewId}`);
    return res.data;
  },

  // Competencies
  getCompetencies: async (orgId: string) => {
    const res = await apiClient.get<Competency[]>(`/api/v1/competencies?org_id=${orgId}`);
    return res.data;
  },
  createCompetency: async (data: Partial<Competency>) => {
    const res = await apiClient.post<Competency>('/api/v1/competencies', data);
    return res.data;
  },
  getEmployeeCompetencies: async (employeeId: string) => {
    const res = await apiClient.get<EmployeeCompetency[]>(`/api/v1/employee-competencies?employee_id=${employeeId}`);
    return res.data;
  },
  assignEmployeeCompetency: async (data: Partial<EmployeeCompetency>) => {
    const res = await apiClient.post<EmployeeCompetency>('/api/v1/employee-competencies', data);
    return res.data;
  },

  // Courses & Enrollments
  getCourses: async (orgId: string) => {
    const res = await apiClient.get<TrainingCourse[]>(`/api/v1/courses?org_id=${orgId}`);
    return res.data;
  },
  createCourse: async (data: Partial<TrainingCourse>) => {
    const res = await apiClient.post<TrainingCourse>('/api/v1/courses', data);
    return res.data;
  },
  getEnrollments: async (employeeId: string) => {
    const res = await apiClient.get<CourseEnrollment[]>(`/api/v1/enrollments?employee_id=${employeeId}`);
    return res.data;
  },
  enrollCourse: async (employeeId: string, courseId: string) => {
    const res = await apiClient.post<CourseEnrollment>('/api/v1/enrollments', {
      employee_id: employeeId,
      course_id: courseId,
    });
    return res.data;
  },
  updateEnrollmentProgress: async (enrollmentId: string, completionPercentage: number) => {
    const res = await apiClient.put<CourseEnrollment>(`/api/v1/enrollments/${enrollmentId}/progress`, {
      completion_percentage: completionPercentage,
    });
    return res.data;
  },

  // Training Programs
  getTrainingPrograms: async (orgId: string) => {
    const res = await apiClient.get<TrainingProgram[]>(`/api/v1/training-programs?org_id=${orgId}`);
    return res.data;
  },
  createTrainingProgram: async (data: Partial<TrainingProgram>) => {
    const res = await apiClient.post<TrainingProgram>('/api/v1/training-programs', data);
    return res.data;
  },

  // Certificates & Download
  getCertificates: async (employeeId: string) => {
    const res = await apiClient.get<LearningCertificate[]>(`/api/v1/certificates?employee_id=${employeeId}`);
    return res.data;
  },
  downloadCertificate: (certNumber: string) => {
    return `/api/v1/certificates/${certNumber}/download`;
  },

  // Skill Matrix
  getSkillMatrix: async (employeeId: string) => {
    const res = await apiClient.get<SkillMatrix[]>(`/api/v1/skill-matrix?employee_id=${employeeId}`);
    return res.data;
  },
  createSkillMatrixItem: async (data: Partial<SkillMatrix>) => {
    const res = await apiClient.post<SkillMatrix>('/api/v1/skill-matrix', data);
    return res.data;
  },

  // Dashboards
  getPerformanceDashboard: async (orgId: string, employeeId?: string) => {
    const url = employeeId
      ? `/api/v1/performance/dashboard?org_id=${orgId}&employee_id=${employeeId}`
      : `/api/v1/performance/dashboard?org_id=${orgId}`;
    const res = await apiClient.get<PerformanceDashboardSummary>(url);
    return res.data;
  },
  getTrainingDashboard: async (orgId: string, employeeId?: string) => {
    const url = employeeId
      ? `/api/v1/training/dashboard?org_id=${orgId}&employee_id=${employeeId}`
      : `/api/v1/training/dashboard?org_id=${orgId}`;
    const res = await apiClient.get<TrainingDashboardSummary>(url);
    return res.data;
  },
};
