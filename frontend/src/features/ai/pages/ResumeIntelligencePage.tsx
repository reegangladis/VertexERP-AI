import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { aiApi } from "../api/aiApi";
import { FileText, Sparkles, CheckCircle2, XCircle, Award, Briefcase, GraduationCap } from "lucide-react";

export const ResumeIntelligencePage: React.FC = () => {
  const [role, setRole] = useState("Senior Full-Stack Engineer");
  const [skillsInput, setSkillsInput] = useState("Python, React, TypeScript, PostgreSQL, Docker, Redis");
  const [minExp, setMinExp] = useState(4);
  const [resumeText, setResumeText] = useState(
    `Alex Mercer
Senior Software Engineer with 6 years of professional experience designing and maintaining distributed web applications.
Core competencies include Python, FastAPI, React, TypeScript, and relational databases including PostgreSQL.
Experience with Docker containerization, AWS deployments, and automated CI/CD testing pipelines.
Education: Bachelor of Science in Computer Science, State University.`
  );

  const matchMutation = useMutation({
    mutationFn: aiApi.matchResume,
  });

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    const skillsList = skillsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    matchMutation.mutate({
      resume_text: resumeText,
      target_role: role,
      required_skills: skillsList,
      min_years_experience: minExp,
    });
  };

  const result = matchMutation.data;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
          <FileText className="w-7 h-7 text-indigo-600" />
          <span>AI Resume Intelligence & Semantic Matcher</span>
        </h1>
        <p className="text-sm text-slate-500">
          NLP-driven candidate profile extraction, competency parsing, and job requisition compatibility scoring.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form: Job Description & Candidate Resume */}
        <div className="lg:col-span-6 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="font-bold text-slate-900 text-base">Requisition & Resume Content</h2>
            <p className="text-xs text-slate-500">Define the benchmark position and input candidate profile text.</p>
          </div>

          <form onSubmit={handleAnalyze} className="space-y-3.5 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-600 mb-1">Target Position / Role</label>
                <input
                  type="text"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 text-xs"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-600 mb-1">Min. Required Years Exp</label>
                <input
                  type="number"
                  value={minExp}
                  onChange={(e) => setMinExp(Number(e.target.value))}
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1">
                Required Competencies (Comma-separated)
              </label>
              <input
                type="text"
                value={skillsInput}
                onChange={(e) => setSkillsInput(e.target.value)}
                placeholder="Python, React, PostgreSQL..."
                className="w-full px-3 py-2 border rounded-xl border-slate-200 text-xs"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1">Resume Body / Extracted Text *</label>
              <textarea
                rows={9}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste candidate resume content here..."
                className="w-full px-3 py-2 border rounded-xl border-slate-200 text-xs font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={!resumeText || matchMutation.isPending}
              className="w-full mt-2 py-2.5 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{matchMutation.isPending ? "Extracting & Evaluating Profile..." : "Evaluate Candidate Fit"}</span>
            </button>
          </form>
        </div>

        {/* Right Panel: Match Intelligence Result */}
        <div className="lg:col-span-6 space-y-4">
          {!result && !matchMutation.isPending && (
            <div className="bg-white p-12 rounded-2xl border border-slate-200/80 shadow-sm text-center space-y-3 h-full flex flex-col justify-center items-center">
              <FileText className="w-12 h-12 text-slate-300 mx-auto" />
              <h3 className="font-bold text-slate-700 text-base">Resume Analysis Ready</h3>
              <p className="text-xs text-slate-400 max-w-sm">
                Click "Evaluate Candidate Fit" to extract skills, experience levels, and benchmark semantic alignment.
              </p>
            </div>
          )}

          {result && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Compatibility Score</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-4xl font-extrabold text-indigo-600">{result.match_score_pct}%</span>
                    <span className="text-xs font-bold text-slate-500">Overall Match</span>
                  </div>
                </div>

                <div className="text-right space-y-1">
                  <div className="flex items-center gap-1.5 text-xs text-slate-600 justify-end">
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                    <span>{result.years_experience_detected} Years Exp Detected</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-600 justify-end">
                    <GraduationCap className="w-3.5 h-3.5 text-slate-400" />
                    <span>{result.education_level}</span>
                  </div>
                </div>
              </div>

              {/* AI Strategic Verdict */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-indigo-600" />
                  <span>AI Synthesis & Recommendation</span>
                </div>
                <div className="text-xs text-slate-700 mt-1 font-medium">{result.ai_verdict}</div>
              </div>

              {/* Matched Skills */}
              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Validated Candidate Competencies</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.matching_skills.map((s: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold"
                    >
                      {s}
                    </span>
                  ))}
                  {result.matching_skills.length === 0 && (
                    <span className="text-xs text-slate-400">No matching skills detected.</span>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <XCircle className="w-3.5 h-3.5 text-rose-600" />
                  <span>Skill Gaps for Requisition</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.missing_skills.map((s: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold"
                    >
                      {s}
                    </span>
                  ))}
                  {result.missing_skills.length === 0 && (
                    <span className="text-xs text-emerald-600 font-medium">100% core skill coverage achieved!</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
