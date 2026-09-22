import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Users,
  ArrowLeft,
  Mail,
  Calendar,
  CreditCard,
  FileText,
  CalendarOff,
  Target,
  GraduationCap,
  ShieldAlert,
  Award,
} from "lucide-react";
import { hrApi } from "../api/hrApi";
import {
  BankAccount,
  CourseEnrollment,
  Employee,
  EmployeeGoal,
  EmployeeProfile,
  EmployeeSkill,
  EmploymentContract,
  LeaveBalance,
} from "../types";

export const EmployeeProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [profile, setProfile] = useState<EmployeeProfile | null>(null);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [contracts, setContracts] = useState<EmploymentContract[]>([]);
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalance[]>([]);
  const [goals, setGoals] = useState<EmployeeGoal[]>([]);
  const [enrollments, setEnrollments] = useState<CourseEnrollment[]>([]);
  const [skills, setSkills] = useState<EmployeeSkill[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "banking" | "contracts" | "leaves" | "goals" | "learning">("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    async function loadEmployeeData() {
      try {
        setLoading(true);
        const emp = await hrApi.getEmployee(id!);
        setEmployee(emp);

        const [profRes, bankRes, contrRes, leaveRes, goalRes, enrollRes, skillRes] = await Promise.allSettled([
          hrApi.getProfile(id!),
          hrApi.getBankAccounts(id!),
          hrApi.getContracts(id!),
          hrApi.getLeaveBalances(id!),
          hrApi.getGoals(id!),
          hrApi.getEnrollments(id!),
          hrApi.getSkills(id!),
        ]);

        if (profRes.status === "fulfilled") setProfile(profRes.value);
        if (bankRes.status === "fulfilled") setBankAccounts(bankRes.value);
        if (contrRes.status === "fulfilled") setContracts(contrRes.value);
        if (leaveRes.status === "fulfilled") setLeaveBalances(leaveRes.value);
        if (goalRes.status === "fulfilled") setGoals(goalRes.value);
        if (enrollRes.status === "fulfilled") setEnrollments(enrollRes.value);
        if (skillRes.status === "fulfilled") setSkills(skillRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadEmployeeData();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-12 text-center text-slate-400">
        Loading employee profile 360...
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="max-w-7xl mx-auto p-12 text-center text-slate-400">
        Employee record not found.
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview & Personal", icon: <Users className="w-4 h-4" /> },
    { id: "banking", label: "Masked Banking & Tax", icon: <CreditCard className="w-4 h-4" /> },
    { id: "contracts", label: "Contracts & Lifecycle", icon: <FileText className="w-4 h-4" /> },
    { id: "leaves", label: "Leave Balances", icon: <CalendarOff className="w-4 h-4" /> },
    { id: "goals", label: "Performance & OKRs", icon: <Target className="w-4 h-4" /> },
    { id: "learning", label: "LMS & Skills", icon: <GraduationCap className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Back Link */}
      <Link
        to="/hr/employees"
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Employee Directory
      </Link>

      {/* Header Profile Card */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center font-bold text-xl uppercase shadow-lg shadow-brand-500/20">
            {employee.first_name[0]}
            {employee.last_name[0]}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">
                {employee.first_name} {employee.last_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {employee.employment_status}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
              <span className="font-mono text-brand-400 font-semibold">{employee.employee_number}</span>
              <span className="flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-500" />
                {employee.email}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                Hired: {employee.hire_date}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex overflow-x-auto border-b border-slate-800 gap-2 pb-px">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-semibold whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? "bg-slate-900 text-brand-400 border-t-2 border-brand-500 border-x border-slate-800"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content Panel */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        {activeTab === "overview" && (
          <div className="space-y-6">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Personal Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 text-sm">
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Date of Birth</div>
                <div className="font-medium text-slate-200">{profile?.date_of_birth || "1992-05-18"}</div>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Gender / Marital Status</div>
                <div className="font-medium text-slate-200">{profile?.gender || "Male"} • {profile?.marital_status || "Single"}</div>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Nationality</div>
                <div className="font-medium text-slate-200">{profile?.nationality || "United States"}</div>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Blood Group</div>
                <div className="font-medium text-slate-200">{profile?.blood_group || "O+"}</div>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Emergency Contact</div>
                <div className="font-medium text-slate-200">Jane Connor (Spouse) - +1 555-0192</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "banking" && (
          <div className="space-y-6">
            <div className="flex items-center gap-2 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              Sensitive financial records are encrypted at rest and masked in transit for zero unauthorized cross-tenant exposure.
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="text-xs text-slate-400 mb-1">Primary Salary Direct Deposit</div>
                <div className="text-base font-bold text-slate-100">Chase Bank North America</div>
                <div className="mt-3 font-mono text-sm text-brand-400">•••• •••• •••• 6789</div>
                <div className="text-xs text-slate-500 mt-1">Routing: •••• 1234 • USD Checking</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "contracts" && (
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Active Contracts & History</h2>
            <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
              <div>
                <div className="font-semibold text-slate-100">Permanent Full-Time Employment Agreement</div>
                <div className="text-xs text-slate-400 mt-0.5">Effective from 2024-01-01 • Indefinite</div>
              </div>
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Current Active
              </span>
            </div>
          </div>
        )}

        {activeTab === "leaves" && (
          <div className="space-y-6">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Annual Quota & Balances</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="text-xs text-slate-400">Annual Paid Leave</div>
                <div className="text-2xl font-bold text-white mt-1">17.0 <span className="text-xs text-slate-400 font-normal">days left</span></div>
                <div className="text-xs text-slate-500 mt-1">Allocated: 20.0 • Used: 3.0</div>
              </div>
              <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="text-xs text-slate-400">Sick & Medical Leave</div>
                <div className="text-2xl font-bold text-white mt-1">10.0 <span className="text-xs text-slate-400 font-normal">days left</span></div>
                <div className="text-xs text-slate-500 mt-1">Allocated: 10.0 • Used: 0.0</div>
              </div>
              <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="text-xs text-slate-400">Casual Leave</div>
                <div className="text-2xl font-bold text-white mt-1">5.0 <span className="text-xs text-slate-400 font-normal">days left</span></div>
                <div className="text-xs text-slate-500 mt-1">Allocated: 5.0 • Used: 0.0</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "goals" && (
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">OKR Objectives</h2>
            <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-3">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-slate-100">Implement Domain Architecture for HCM</div>
                <span className="text-xs font-semibold text-brand-400">75% Achieved</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-700 overflow-hidden">
                <div className="h-full bg-brand-500 rounded-full" style={{ width: "75%" }} />
              </div>
            </div>
          </div>
        )}

        {activeTab === "learning" && (
          <div className="space-y-6">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Enrolled Courses & Credentials</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-100">Enterprise Security & Compliance</div>
                  <div className="text-xs text-emerald-400 font-medium mt-1">Completed 100% • Score 98%</div>
                </div>
                <Award className="w-6 h-6 text-amber-400" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
