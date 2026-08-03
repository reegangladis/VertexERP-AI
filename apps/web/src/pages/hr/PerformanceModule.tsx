import React, { useState, useEffect } from 'react';
import {
  Target,
  Award,
  TrendingUp,
  Star,
  Plus,
  CheckCircle2,
  Users,
  Search,
  Zap,
  BarChart3,
  Calendar,
  MessageSquare,
  ShieldCheck,
  ChevronRight,
  Sparkles,
  Layers,
  ArrowUpRight,
  Filter,
} from 'lucide-react';
import { performanceLearningService, Goal, PerformanceReview, PerformanceReviewCycle, Competency, SkillMatrix, PerformanceDashboardData } from '@/services/performanceLearning';

export function PerformanceModule() {
  const [activeTab, setActiveTab] = useState<'overview' | 'goals' | 'reviews' | 'feedback' | 'competencies'>('overview');
  const [goals, setGoals] = useState<Goal[]>([]);
  const [reviewCycles, setReviewCycles] = useState<PerformanceReviewCycle[]>([]);
  const [reviews, setReviews] = useState<PerformanceReview[]>([]);
  const [competencies, setCompetencies] = useState<Competency[]>([]);
  const [skillMatrix, setSkillMatrix] = useState<SkillMatrix[]>([]);
  const [dashboardData, setDashboardData] = useState<PerformanceDashboardData | null>(null);

  // Modals
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [selectedReviewId, setSelectedReviewId] = useState<string>('');

  // Form states
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [newGoalDesc, setNewGoalDesc] = useState('');
  const [newGoalType, setNewGoalType] = useState('OKR');
  const [newGoalPriority, setNewGoalPriority] = useState('High');
  const [newGoalStartDate, setNewGoalStartDate] = useState('2026-07-01');
  const [newGoalEndDate, setNewGoalEndDate] = useState('2026-09-30');

  const [feedbackType, setFeedbackType] = useState('Self');
  const [feedbackRating, setFeedbackRating] = useState(5.0);
  const [feedbackComments, setFeedbackComments] = useState('');

  const sampleOrgId = 'org-101-demo';
  const sampleEmployeeId = 'emp-808-demo';

  const loadData = async () => {
    try {
      const [gData, cData, rData, compData, matrixData, dash] = await Promise.all([
        performanceLearningService.getGoals(sampleEmployeeId).catch(() => []),
        performanceLearningService.getReviewCycles(sampleOrgId).catch(() => []),
        performanceLearningService.getReviews(sampleEmployeeId).catch(() => []),
        performanceLearningService.getCompetencies(sampleOrgId).catch(() => []),
        performanceLearningService.getSkillMatrix(sampleEmployeeId).catch(() => []),
        performanceLearningService.getPerformanceDashboard(sampleOrgId, sampleEmployeeId).catch(() => null),
      ]);

      setGoals(gData.length ? gData : mockGoals);
      setReviewCycles(cData.length ? cData : mockCycles);
      setReviews(rData.length ? rData : mockReviews);
      setCompetencies(compData.length ? compData : mockCompetencies);
      setSkillMatrix(matrixData.length ? matrixData : mockSkillMatrix);
      setDashboardData(dash || mockDashboard);
    } catch (e) {
      console.error('Failed to load performance data:', e);
      setGoals(mockGoals);
      setReviewCycles(mockCycles);
      setReviews(mockReviews);
      setCompetencies(mockCompetencies);
      setSkillMatrix(mockSkillMatrix);
      setDashboardData(mockDashboard);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await performanceLearningService.createGoal({
        organization_id: sampleOrgId,
        employee_id: sampleEmployeeId,
        title: newGoalTitle,
        description: newGoalDesc,
        goal_type: newGoalType,
        priority: newGoalPriority,
        start_date: newGoalStartDate,
        end_date: newGoalEndDate,
        status: 'In Progress',
        progress: 0.0,
      });
      setIsGoalModalOpen(false);
      loadData();
    } catch (err) {
      console.error('Create Goal Error', err);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await performanceLearningService.submitFeedback({
        review_id: selectedReviewId || (reviews[0]?.id || 'rev-1'),
        feedback_type: feedbackType,
        rating: feedbackRating,
        comments: feedbackComments,
        submitted_by: sampleEmployeeId,
      });
      setIsFeedbackModalOpen(false);
      loadData();
    } catch (err) {
      console.error('Feedback error', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 rounded-2xl p-6 text-white shadow-2xl border border-indigo-500/20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" /> Phase 9 — Enterprise Performance & Learning Platform
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">Performance Management & OKRs</h1>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Align organizational goals, evaluate 360-degree performance feedback, track competency gap matrix, and calculate automated promotion readiness scores.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsGoalModalOpen(true)}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
            >
              <Plus className="w-4 h-4" /> Create Goal (OKR)
            </button>
            <button
              onClick={() => setIsFeedbackModalOpen(true)}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-sm font-medium flex items-center gap-2 transition-all"
            >
              <MessageSquare className="w-4 h-4 text-emerald-400" /> Submit 360 Feedback
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-800 overflow-x-auto">
          {[
            { id: 'overview', label: 'Performance Overview', icon: BarChart3 },
            { id: 'goals', label: 'Goals & OKRs', icon: Target },
            { id: 'reviews', label: 'Review Cycles & Ratings', icon: Award },
            { id: 'feedback', label: '360° Feedback', icon: MessageSquare },
            { id: 'competencies', label: 'Competencies & Skill Matrix', icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-indigo-600/90 text-white shadow-md shadow-indigo-900/40 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden group">
              <div className="absolute right-3 top-3 p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
                <Target className="w-6 h-6" />
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Goal Progress</div>
              <div className="text-3xl font-black text-white mt-2">
                {dashboardData?.average_goal_progress || 82.5}%
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-blue-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${dashboardData?.average_goal_progress || 82.5}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-2 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                {dashboardData?.completed_goals || 4} of {dashboardData?.total_goals || 6} Goals Completed
              </p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden group">
              <div className="absolute right-3 top-3 p-2 bg-amber-500/10 rounded-lg text-amber-400">
                <Star className="w-6 h-6" />
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Performance Rating</div>
              <div className="text-3xl font-black text-white mt-2 flex items-baseline gap-2">
                {dashboardData?.average_performance_rating || 4.75} <span className="text-sm text-slate-400 font-normal">/ 5.0</span>
              </div>
              <div className="flex items-center gap-1 mt-2">
                {[1, 2, 3, 4, 5].map((s) => (
                  <Star key={s} className={`w-4 h-4 ${s <= 4.75 ? 'text-amber-400 fill-amber-400' : 'text-slate-700'}`} />
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-2">Annual Evaluation Grade: Exceeds Expectations</p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden group">
              <div className="absolute right-3 top-3 p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Promotion Readiness Score</div>
              <div className="text-3xl font-black text-emerald-400 mt-2">
                {dashboardData?.promotion_readiness_score || 92.4}%
              </div>
              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mt-2">
                High Promotion Potential
              </div>
              <p className="text-xs text-slate-400 mt-2">Recommended for Senior Staff Engineer upgrade</p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden group">
              <div className="absolute right-3 top-3 p-2 bg-purple-500/10 rounded-lg text-purple-400">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Review Cycles</div>
              <div className="text-3xl font-black text-white mt-2">
                {dashboardData?.active_review_cycles || 2} Active
              </div>
              <p className="text-xs text-slate-400 mt-3 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-purple-400" />
                {dashboardData?.pending_reviews || 1} Pending Feedback Reviews
              </p>
            </div>
          </div>

          {/* Goals & Ratings Section Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Target className="w-5 h-5 text-indigo-400" /> Key OKRs & Performance Objectives
                </h3>
                <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Q3 2026 Active Goals</span>
              </div>
              <div className="space-y-4">
                {goals.map((g) => (
                  <div key={g.id} className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 hover:border-indigo-500/40 transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-bold ${g.priority === 'High' ? 'bg-rose-500/20 text-rose-300' : 'bg-blue-500/20 text-blue-300'}`}>
                            {g.priority} Priority
                          </span>
                          <span className="text-xs text-slate-400 font-mono">{g.goal_type}</span>
                        </div>
                        <h4 className="text-base font-semibold text-white mt-1">{g.title}</h4>
                        <p className="text-xs text-slate-300 mt-0.5">{g.description}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-lg font-bold text-indigo-300">{g.progress}%</span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded-full mt-3 overflow-hidden">
                      <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${g.progress}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Trends Widget */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-emerald-400" /> Evaluation Trends
              </h3>
              <div className="space-y-4">
                {(dashboardData?.performance_trends || mockDashboard.performance_trends).map((t, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-800/40 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-semibold text-white">{t.period}</div>
                      <div className="text-xs text-slate-400">Goal Completion: {t.goalCompletion}%</div>
                    </div>
                    <div className="flex items-center gap-1 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                      <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                      <span className="text-xs font-bold text-amber-300">{t.rating}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 rounded-xl bg-indigo-950/40 border border-indigo-800/50">
                <div className="text-xs font-bold text-indigo-300 uppercase tracking-wider">AI Executive Assessment</div>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                  Consistently delivers high-value OKRs and demonstrates exceptional architectural leadership. Ready for executive review.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Goals Tab */}
      {activeTab === 'goals' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Target className="w-6 h-6 text-indigo-400" /> Goals & Objectives (OKRs)
            </h3>
            <button
              onClick={() => setIsGoalModalOpen(true)}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" /> Add OKR
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {goals.map((goal) => (
              <div key={goal.id} className="p-5 bg-slate-800/50 rounded-xl border border-slate-700 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    {goal.goal_type} • Weight: {goal.weightage}%
                  </span>
                  <span className="text-xs font-bold text-slate-400">{goal.start_date} to {goal.end_date}</span>
                </div>
                <h4 className="text-lg font-bold text-white">{goal.title}</h4>
                <p className="text-xs text-slate-300">{goal.description}</p>
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>Progress</span>
                    <span className="text-indigo-400">{goal.progress}%</span>
                  </div>
                  <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full" style={{ width: `${goal.progress}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reviews Tab */}
      {activeTab === 'reviews' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Award className="w-6 h-6 text-amber-400" /> Performance Review Cycles
          </h3>
          <div className="space-y-4">
            {reviewCycles.map((cycle) => (
              <div key={cycle.id} className="p-5 bg-slate-800/40 rounded-xl border border-slate-700 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-300">{cycle.review_type}</span>
                    <span className="text-xs text-slate-400 font-mono">Cycle ID: {cycle.id}</span>
                  </div>
                  <h4 className="text-lg font-bold text-white mt-1">{cycle.name}</h4>
                  <p className="text-xs text-slate-400">Timeline: {cycle.start_date} — {cycle.end_date}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Status: {cycle.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 360 Feedback Tab */}
      {activeTab === 'feedback' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-purple-400" /> 360 Degree Feedback Center
            </h3>
            <button
              onClick={() => setIsFeedbackModalOpen(true)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" /> Submit Feedback
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-800/40 rounded-xl border border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-purple-500/20 text-purple-300">Self Assessment</span>
                <span className="text-xs text-amber-400 font-bold">★ 4.8 / 5.0</span>
              </div>
              <p className="text-xs text-slate-300 italic">"Architected cloud-native services for VertexERP AI Phase 1-9 with 100% test coverage."</p>
            </div>
            <div className="p-4 bg-slate-800/40 rounded-xl border border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-blue-500/20 text-blue-300">Manager Assessment</span>
                <span className="text-xs text-amber-400 font-bold">★ 5.0 / 5.0</span>
              </div>
              <p className="text-xs text-slate-300 italic">"Outstanding engineering output, leadership, and cross-functional execution."</p>
            </div>
          </div>
        </div>
      )}

      {/* Competencies Tab */}
      {activeTab === 'competencies' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" /> Skill Matrix & Competency Tracking
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {skillMatrix.map((item, idx) => (
              <div key={idx} className="p-4 bg-slate-800/40 rounded-xl border border-slate-700 space-y-2">
                <span className="text-xs font-mono text-indigo-400">{item.category}</span>
                <h4 className="text-base font-bold text-white">{item.skill_name}</h4>
                <div className="flex items-center justify-between text-xs text-slate-300 pt-2 border-t border-slate-700">
                  <span>Current: <strong className="text-emerald-400">{item.current_level}</strong></span>
                  <span>Target: <strong className="text-indigo-400">{item.target_level}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal: Create Goal */}
      {isGoalModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl text-white space-y-4">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Target className="w-5 h-5 text-indigo-400" /> Create New Goal (OKR)
            </h3>
            <form onSubmit={handleCreateGoal} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300">Goal Title</label>
                <input
                  type="text"
                  required
                  value={newGoalTitle}
                  onChange={(e) => setNewGoalTitle(e.target.value)}
                  className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. Expand microservices test coverage"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300">Description</label>
                <textarea
                  value={newGoalDesc}
                  onChange={(e) => setNewGoalDesc(e.target.value)}
                  className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300">Goal Type</label>
                  <select
                    value={newGoalType}
                    onChange={(e) => setNewGoalType(e.target.value)}
                    className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                  >
                    <option value="OKR">OKR</option>
                    <option value="KPI">KPI</option>
                    <option value="Personal">Personal Development</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300">Priority</label>
                  <select
                    value={newGoalPriority}
                    onChange={(e) => setNewGoalPriority(e.target.value)}
                    className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300">Start Date</label>
                  <input
                    type="date"
                    value={newGoalStartDate}
                    onChange={(e) => setNewGoalStartDate(e.target.value)}
                    className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300">End Date</label>
                  <input
                    type="date"
                    value={newGoalEndDate}
                    onChange={(e) => setNewGoalEndDate(e.target.value)}
                    className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsGoalModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold"
                >
                  Save Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: 360 Feedback */}
      {isFeedbackModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl text-white space-y-4">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-purple-400" /> Submit Performance Feedback
            </h3>
            <form onSubmit={handleSubmitFeedback} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300">Feedback Type</label>
                <select
                  value={feedbackType}
                  onChange={(e) => setFeedbackType(e.target.value)}
                  className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                >
                  <option value="Self">Self Assessment</option>
                  <option value="Manager">Manager Review</option>
                  <option value="Peer">Peer Evaluation</option>
                  <option value="360">360 Feedback</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300">Rating (1.0 to 5.0)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={feedbackRating}
                  onChange={(e) => setFeedbackRating(parseFloat(e.target.value))}
                  className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300">Comments & Evaluation</label>
                <textarea
                  required
                  value={feedbackComments}
                  onChange={(e) => setFeedbackComments(e.target.value)}
                  className="w-full mt-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white"
                  rows={3}
                  placeholder="Provide detailed feedback..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsFeedbackModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-semibold"
                >
                  Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Fallback Mock Data for preview & robustness
const mockGoals: Goal[] = [
  {
    id: 'g-1',
    organization_id: 'org-1',
    employee_id: 'emp-1',
    title: 'Architect Enterprise AI LMS Subsystem (Phase 9)',
    description: 'Implement complete backend & frontend engines for goals, reviews, feedback, and skill matrix.',
    goal_type: 'OKR',
    priority: 'High',
    weightage: 100.0,
    start_date: '2026-07-01',
    end_date: '2026-09-30',
    status: 'In Progress',
    progress: 90.0,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-01T00:00:00Z',
  },
];

const mockCycles: PerformanceReviewCycle[] = [
  {
    id: 'c-1',
    organization_id: 'org-1',
    name: '2026 Annual Enterprise Evaluation',
    review_type: 'Annual',
    start_date: '2026-01-01',
    end_date: '2026-12-31',
    status: 'Active',
  },
];

const mockReviews: PerformanceReview[] = [
  {
    id: 'rev-1',
    employee_id: 'emp-1',
    review_cycle_id: 'c-1',
    reviewer_id: 'emp-mgr',
    overall_rating: 4.85,
    overall_score: 97.0,
    status: 'Submitted',
  },
];

const mockCompetencies: Competency[] = [
  { id: 'comp-1', organization_id: 'org-1', name: 'Software Architecture', category: 'Technical' },
  { id: 'comp-2', organization_id: 'org-1', name: 'Enterprise Domain Design', category: 'Core' },
];

const mockSkillMatrix: SkillMatrix[] = [
  { id: 's-1', employee_id: 'emp-1', skill_name: 'Python & FastAPI', category: 'Backend', current_level: 'Expert', target_level: 'Expert', last_updated: '2026-08-01' },
  { id: 's-2', employee_id: 'emp-1', skill_name: 'SQLAlchemy & Alembic', category: 'Database', current_level: 'Advanced', target_level: 'Expert', last_updated: '2026-08-01' },
];

const mockDashboard: PerformanceDashboardData = {
  total_goals: 4,
  completed_goals: 3,
  average_goal_progress: 90.0,
  active_review_cycles: 1,
  pending_reviews: 0,
  average_performance_rating: 4.85,
  promotion_readiness_score: 95.0,
  performance_trends: [
    { period: 'Q1 2026', rating: 4.6, goalCompletion: 85 },
    { period: 'Q2 2026', rating: 4.8, goalCompletion: 92 },
    { period: 'Q3 2026', rating: 4.85, goalCompletion: 95 },
  ],
};
