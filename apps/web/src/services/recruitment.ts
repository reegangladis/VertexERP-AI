import { apiClient } from './apiClient';

export interface JobRequisition {
  id: string;
  organization_id: string;
  department_id?: string;
  designation_id?: string;
  requested_by?: string;
  approved_by?: string;
  title: string;
  job_code: string;
  employment_type: string;
  vacancies: number;
  priority: string;
  budget: number;
  status: string;
  opening_date?: string;
  closing_date?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface JobPosting {
  id: string;
  requisition_id: string;
  title: string;
  description: string;
  location?: string;
  employment_type: string;
  experience_required?: string;
  salary_range?: string;
  published: boolean;
  published_at?: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Candidate {
  id: string;
  organization_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  resume_url?: string;
  current_company?: string;
  current_designation?: string;
  experience_years: number;
  expected_salary: number;
  notice_period?: string;
  source: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewFeedback {
  id: string;
  interview_round_id: string;
  interviewer_id?: string;
  technical_rating: number;
  communication_rating: number;
  problem_solving_rating: number;
  overall_rating: number;
  strengths?: string;
  weaknesses?: string;
  recommendation: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewRound {
  id: string;
  application_id: string;
  round_name: string;
  round_type: string;
  interviewer_id?: string;
  scheduled_date: string;
  duration: number;
  meeting_link?: string;
  status: string;
  feedback: InterviewFeedback[];
  created_at: string;
  updated_at: string;
}

export interface JobOffer {
  id: string;
  application_id: string;
  offered_ctc: number;
  joining_date: string;
  offer_letter_url?: string;
  status: string;
  accepted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: string;
  candidate_id: string;
  job_posting_id: string;
  application_date: string;
  current_stage: string;
  status: string;
  rating: number;
  remarks?: string;
  interview_rounds: InterviewRound[];
  offers: JobOffer[];
  created_at: string;
  updated_at: string;
}

export interface RecruitmentSummary {
  open_positions_count: number;
  active_candidates_count: number;
  interviews_today_count: number;
  pending_offers_count: number;
  accepted_offers_count: number;
  avg_time_to_hire_days: number;
  funnel_stage_counts: Record<string, number>;
}

export const recruitmentService = {
  // Requisitions & Postings
  listRequisitions: async (orgId: string): Promise<JobRequisition[]> => {
    const res = await apiClient.get(`/api/v1/recruitment/requisitions?org_id=${orgId}`);
    return res.data;
  },

  createRequisition: async (payload: Partial<JobRequisition>): Promise<JobRequisition> => {
    const res = await apiClient.post('/api/v1/recruitment/requisitions', payload);
    return res.data;
  },

  approveRequisition: async (id: string, approverId: string): Promise<JobRequisition> => {
    const res = await apiClient.post(`/api/v1/recruitment/requisitions/${id}/approve?approver_id=${approverId}`);
    return res.data;
  },

  listPostings: async (): Promise<JobPosting[]> => {
    const res = await apiClient.get('/api/v1/recruitment/postings');
    return res.data;
  },

  createPosting: async (payload: Partial<JobPosting>): Promise<JobPosting> => {
    const res = await apiClient.post('/api/v1/recruitment/postings', payload);
    return res.data;
  },

  // Candidates & Applications
  listCandidates: async (orgId: string): Promise<Candidate[]> => {
    const res = await apiClient.get(`/api/v1/recruitment/candidates?org_id=${orgId}`);
    return res.data;
  },

  createCandidate: async (payload: Partial<Candidate>): Promise<Candidate> => {
    const res = await apiClient.post('/api/v1/recruitment/candidates', payload);
    return res.data;
  },

  applyForJob: async (payload: { candidate_id: string; job_posting_id: string; remarks?: string }): Promise<Application> => {
    const res = await apiClient.post('/api/v1/recruitment/applications', payload);
    return res.data;
  },

  updateStage: async (id: string, payload: { current_stage: string; status?: string; remarks?: string }): Promise<Application> => {
    const res = await apiClient.post(`/api/v1/recruitment/applications/${id}/stage`, payload);
    return res.data;
  },

  // Interviews
  scheduleInterview: async (payload: Partial<InterviewRound>): Promise<InterviewRound> => {
    const res = await apiClient.post('/api/v1/recruitment/interviews', payload);
    return res.data;
  },

  submitFeedback: async (payload: Partial<InterviewFeedback>): Promise<InterviewFeedback> => {
    const res = await apiClient.post('/api/v1/recruitment/interviews/feedback', payload);
    return res.data;
  },

  // Offers
  createOffer: async (payload: Partial<JobOffer>): Promise<JobOffer> => {
    const res = await apiClient.post('/api/v1/recruitment/offers', payload);
    return res.data;
  },

  updateOfferStatus: async (id: string, payload: { status: string }): Promise<JobOffer> => {
    const res = await apiClient.post(`/api/v1/recruitment/offers/${id}/action`, payload);
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<RecruitmentSummary> => {
    const res = await apiClient.get(`/api/v1/recruitment/dashboard-summary?org_id=${orgId}`);
    return res.data;
  },
};
