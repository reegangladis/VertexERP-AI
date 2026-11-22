import React, { useEffect, useState } from "react";
import { GraduationCap, Award, BookOpen, CheckCircle, Clock } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { TrainingCourse } from "../types";

export const LearningPage: React.FC = () => {
  const [courses, setCourses] = useState<TrainingCourse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLMS() {
      try {
        const cRes = await hrApi.getCourses();
        setCourses(cRes);
      } catch (err) {
        console.error("Failed to load courses", err);
      } finally {
        setLoading(false);
      }
    }
    loadLMS();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <GraduationCap className="w-6 h-6 text-blue-400" />
          Learning & Talent Development (LMS)
        </h1>
        <p className="text-slate-400 text-sm mt-0.5">
          Training course catalog, syllabus modules, employee certifications, and talent skill matrices.
        </p>
      </div>

      {/* Course Catalog Grid */}
      <div>
        <h2 className="text-base font-bold text-white mb-3">Enterprise Course Catalog</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400">COMPLIANCE</span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> 2.5 Hours
              </span>
            </div>
            <div className="font-semibold text-slate-100">Enterprise Security & Multi-Tenant Compliance</div>
            <p className="text-xs text-slate-400">SOC2 compliance, secure key storage, and zero data leakage isolation rules.</p>
            <div className="pt-2 border-t border-slate-800 text-xs text-slate-500">
              3 syllabus modules • Mandatory
            </div>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400">TECHNICAL</span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> 10.0 Hours
              </span>
            </div>
            <div className="font-semibold text-slate-100">Advanced Async Python & Microservices</div>
            <p className="text-xs text-slate-400">Clean architecture, PostgreSQL async session isolation, and resilient testing.</p>
            <div className="pt-2 border-t border-slate-800 text-xs text-slate-500">
              5 syllabus modules • Elective
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
