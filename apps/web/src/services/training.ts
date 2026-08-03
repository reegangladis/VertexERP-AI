import { apiClient } from './apiClient';

export interface CourseModule {
  id: string;
  course_id: string;
  module_name: string;
  module_order: number;
  duration_minutes: number;
  content_url?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Assessment {
  id: string;
  course_id: string;
  assessment_name: string;
  passing_score: number;
  total_marks: number;
  duration_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface TrainingCourse {
  id: string;
  organization_id: string;
  course_code: string;
  course_name: string;
  description?: string;
  category: string;
  difficulty_level: string;
  duration_hours: number;
  delivery_mode: string;
  status: string;
  modules: CourseModule[];
  assessments: Assessment[];
  created_at: string;
  updated_at: string;
}

export interface Certification {
  id: string;
  employee_training_id: string;
  certificate_number: string;
  issued_date: string;
  expiry_date?: string;
  certificate_url?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeTraining {
  id: string;
  employee_id: string;
  course_id: string;
  assigned_date: string;
  due_date?: string;
  completed_date?: string;
  completion_percentage: number;
  status: string;
  certifications: Certification[];
  created_at: string;
  updated_at: string;
}

export interface AssessmentAttempt {
  id: string;
  assessment_id: string;
  employee_id: string;
  score: number;
  attempt_number: number;
  passed: boolean;
  submitted_at: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeSkill {
  id: string;
  employee_id: string;
  skill_name: string;
  skill_level: string;
  verified: boolean;
  last_updated: string;
  created_at: string;
  updated_at: string;
}

export interface TrainingSummary {
  assigned_courses_count: number;
  completed_courses_count: number;
  pending_courses_count: number;
  certificates_earned_count: number;
  total_learning_hours: number;
  upcoming_sessions_count: number;
  skill_compliance_rate: number;
}

export const trainingService = {
  // Courses & Modules
  listCourses: async (orgId: string): Promise<TrainingCourse[]> => {
    const res = await apiClient.get(`/api/v1/training/courses?org_id=${orgId}`);
    return res.data;
  },

  createCourse: async (payload: Partial<TrainingCourse>): Promise<TrainingCourse> => {
    const res = await apiClient.post('/api/v1/training/courses', payload);
    return res.data;
  },

  createModule: async (courseId: string, payload: Partial<CourseModule>): Promise<CourseModule> => {
    const res = await apiClient.post(`/api/v1/training/courses/${courseId}/modules`, payload);
    return res.data;
  },

  // Enrollments & Progress
  assignTraining: async (payload: { employee_id: string; course_id: string; due_date?: string }): Promise<EmployeeTraining> => {
    const res = await apiClient.post('/api/v1/training/assign', payload);
    return res.data;
  },

  updateProgress: async (id: string, completion_percentage: number): Promise<EmployeeTraining> => {
    const res = await apiClient.post(`/api/v1/training/trainings/${id}/progress`, { completion_percentage });
    return res.data;
  },

  listEmployeeTrainings: async (employeeId: string): Promise<EmployeeTraining[]> => {
    const res = await apiClient.get(`/api/v1/training/employee-trainings?employee_id=${employeeId}`);
    return res.data;
  },

  // Assessments
  submitAssessment: async (assessmentId: string, payload: { employee_id: string; score: number }): Promise<AssessmentAttempt> => {
    const res = await apiClient.post(`/api/v1/training/assessments/${assessmentId}/submit`, payload);
    return res.data;
  },

  // Skills
  listSkills: async (employeeId: string): Promise<EmployeeSkill[]> => {
    const res = await apiClient.get(`/api/v1/training/skills?employee_id=${employeeId}`);
    return res.data;
  },

  addSkill: async (payload: Partial<EmployeeSkill>): Promise<EmployeeSkill> => {
    const res = await apiClient.post('/api/v1/training/skills', payload);
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (orgId: string, employeeId: string): Promise<TrainingSummary> => {
    const res = await apiClient.get(`/api/v1/training/dashboard-summary?org_id=${orgId}&employee_id=${employeeId}`);
    return res.data;
  },
};
