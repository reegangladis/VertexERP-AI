import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  BookOpen,
  Award,
  Calendar,
  CheckCircle2,
  Clock,
  PlayCircle,
  FileText,
  Plus,
  Search,
  Check,
  Star,
  Users,
  Target,
  Download,
  TrendingUp,
  Layers,
  ChevronRight,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { performanceLearningService, TrainingCourse, CourseEnrollment, LearningCertificate } from '@/services/performanceLearning';

const mockCourses = [
  { id: 'c1', code: 'SEC-101', name: 'Cybersecurity & Data Privacy 2026', category: 'Compliance', level: 'Intermediate', duration: '4.5 hrs', mode: 'Online', modulesCount: 4, rating: 4.9 },
  { id: 'c2', name: 'Cloud Native Microservices Architecture', category: 'Engineering', level: 'Advanced', duration: '12.0 hrs', mode: 'Self-paced', modulesCount: 8, rating: 4.8 },
  { id: 'c3', name: 'Enterprise Agile Leadership & Scrum', category: 'Management', level: 'Intermediate', duration: '6.0 hrs', mode: 'Hybrid', modulesCount: 5, rating: 4.7 },
];

const mockMyTrainings = [
  { id: 't1', course: 'Cybersecurity & Data Privacy 2026', code: 'SEC-101', assigned: '2026-07-15', due: '2026-08-15', progress: 100, status: 'Completed', certNo: 'CERT-SEC-202607-88A1' },
  { id: 't2', course: 'Cloud Native Microservices Architecture', code: 'ENG-302', assigned: '2026-08-01', due: '2026-09-01', progress: 45, status: 'In Progress', certNo: null },
];

const mockSkillMatrix = [
  { skill: 'Python Architecture', reqLevel: 'Advanced', currLevel: 'Advanced', status: 'Compliant' },
  { skill: 'Cybersecurity Audit', reqLevel: 'Advanced', currLevel: 'Intermediate', status: 'Gap Identified' },
  { skill: 'Agile Coaching', reqLevel: 'Intermediate', currLevel: 'Intermediate', status: 'Compliant' },
];

export function TrainingModule() {
  const [activeTab, setActiveTab] = useState<'overview' | 'catalog' | 'my_training' | 'certificates' | 'skills' | 'sessions'>('overview');
  const [isAddCourseModalOpen, setIsAddCourseModalOpen] = useState(false);
  const [courseName, setCourseName] = useState('');
  const [courseCategory, setCourseCategory] = useState('Compliance');
  const [deliveryMode, setDeliveryMode] = useState('Online');

  const [courses, setCourses] = useState<any[]>(mockCourses);
  const [certificates, setCertificates] = useState<any[]>([]);

  useEffect(() => {
    performanceLearningService.getCourses('org-101-demo')
      .then((res) => { if (res && res.length) setCourses(res); })
      .catch(() => {});
    performanceLearningService.getCertificates('emp-808-demo')
      .then((res) => { if (res) setCertificates(res); })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 rounded-xl p-6 text-white shadow-xl border border-blue-900/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-blue-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <GraduationCap className="w-4 h-4" /> Phase 9 — Enterprise Learning & Development (L&D) Platform
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Learning & Skill Development LMS</h1>
            <p className="text-sm text-slate-300 mt-1">
              Onboarding courses, learning paths, quizzes, automated certificate generation & designation skill gap matrix.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsAddCourseModalOpen(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" /> Create Course
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 overflow-x-auto border-t border-slate-800/80 pt-4 scrollbar-none">
          {[
            { id: 'overview', label: 'Learning Dashboard', icon: <TrendingUp className="w-3.5 h-3.5" /> },
            { id: 'catalog', label: 'Course Catalog', icon: <BookOpen className="w-3.5 h-3.5" /> },
            { id: 'my_training', label: 'My Enrolled Training', icon: <PlayCircle className="w-3.5 h-3.5" /> },
            { id: 'certificates', label: 'Earned Certifications', icon: <Award className="w-3.5 h-3.5" /> },
            { id: 'skills', label: 'Skill Matrix & Gap Analysis', icon: <Target className="w-3.5 h-3.5" /> },
            { id: 'sessions', label: 'Instructor Live Sessions', icon: <Calendar className="w-3.5 h-3.5" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 1. OVERVIEW DASHBOARD */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Enrolled Courses</span>
                <BookOpen className="w-4 h-4 text-blue-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">2 Active</h3>
              <p className="text-[10px] text-blue-400 font-mono">1 Completed (100%)</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Certificates Earned</span>
                <Award className="w-4 h-4 text-amber-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">1 Verified</h3>
              <p className="text-[10px] text-amber-500 font-mono">CERT-SEC-202607-88A1</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Total Learning Hours</span>
                <Clock className="w-4 h-4 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">24.5 Hours</h3>
              <p className="text-[10px] text-emerald-500 font-mono">Top 5% Learning Activity</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Skill Matrix Compliance</span>
                <ShieldCheck className="w-4 h-4 text-purple-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">92.5%</h3>
              <p className="text-[10px] text-purple-400 font-mono">2 / 3 Skills Compliant</p>
            </div>
          </div>

          {/* Active Training Progress Cards */}
          <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <PlayCircle className="w-4 h-4 text-blue-500" /> Current Learning Assignments
            </h3>
            <div className="space-y-4">
              {mockMyTrainings.map((tr) => (
                <div key={tr.id} className="p-4 bg-secondary/20 rounded-xl border border-border/60 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 font-mono text-[10px] font-bold rounded">
                          {tr.code}
                        </span>
                        <h4 className="text-xs font-bold text-foreground">{tr.course}</h4>
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-1">Due Date: {tr.due}</p>
                    </div>
                    <span className={`px-2.5 py-1 text-[11px] font-bold rounded-full ${
                      tr.status === 'Completed' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {tr.status}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-muted-foreground font-mono">
                      <span>Progress</span>
                      <span>{tr.progress}%</span>
                    </div>
                    <div className="w-full bg-secondary/50 rounded-full h-2 overflow-hidden">
                      <div className="bg-blue-500 h-full transition-all duration-300" style={{ width: `${tr.progress}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 2. COURSE CATALOG */}
      {activeTab === 'catalog' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground">Available Enterprise Courses</h3>
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Search course title or code..."
                className="p-2 text-xs rounded-lg border border-border bg-background text-foreground w-64"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mockCourses.map((c) => (
              <div key={c.id} className="bg-card p-5 rounded-xl border border-border/70 hover:border-blue-500/50 transition space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-[10px] font-mono font-bold rounded">
                      {c.category}
                    </span>
                    <div className="flex items-center gap-1 text-amber-500 text-xs font-bold">
                      <Star className="w-3 h-3 fill-amber-500" /> {c.rating}
                    </div>
                  </div>
                  <h4 className="text-sm font-bold text-foreground">{c.name}</h4>
                  <div className="flex items-center gap-3 text-[11px] text-muted-foreground font-mono">
                    <span>{c.duration}</span>
                    <span>•</span>
                    <span>{c.level}</span>
                    <span>•</span>
                    <span>{c.mode}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-border/50 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{c.modulesCount} Modules</span>
                  <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition">
                    Enroll Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. SKILL MATRIX & GAP ANALYSIS */}
      {activeTab === 'skills' && (
        <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Target className="w-4 h-4 text-purple-500" /> Designation Skill Matrix & Gap Evaluator
            </h3>
            <span className="text-xs text-muted-foreground font-mono">Designation: Senior Lead Software Architect</span>
          </div>

          <div className="space-y-3">
            {mockSkillMatrix.map((sm, idx) => (
              <div key={idx} className="p-4 bg-secondary/20 rounded-xl border border-border/60 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-foreground">{sm.skill}</h4>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Required Level: <span className="font-semibold text-foreground">{sm.reqLevel}</span> | Current Level: <span className="font-semibold text-foreground">{sm.currLevel}</span>
                  </p>
                </div>
                <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                  sm.status === 'Compliant' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                }`}>
                  {sm.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CREATE COURSE MODAL */}
      {isAddCourseModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-2xl border border-border shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-500" /> Create Training Course
              </h3>
              <button onClick={() => setIsAddCourseModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1">Course Name</label>
                <input
                  type="text"
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                  placeholder="e.g. Advanced AI Model Safety"
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-1">Category</label>
                  <select
                    value={courseCategory}
                    onChange={(e) => setCourseCategory(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  >
                    <option>Compliance</option>
                    <option>Engineering</option>
                    <option>Management</option>
                    <option>Product</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold mb-1">Delivery Mode</label>
                  <select
                    value={deliveryMode}
                    onChange={(e) => setDeliveryMode(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  >
                    <option>Online</option>
                    <option>Offline</option>
                    <option>Hybrid</option>
                    <option>Self-paced</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-border">
              <button
                onClick={() => setIsAddCourseModalOpen(false)}
                className="px-4 py-2 bg-secondary text-foreground text-xs font-semibold rounded-lg hover:bg-secondary/80"
              >
                Cancel
              </button>
              <button
                onClick={() => setIsAddCourseModalOpen(false)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow transition"
              >
                Publish Course
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrainingModule;
