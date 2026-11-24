import React, { useState } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { getInitials } from "@/lib/utils";
import { User, Mail, Phone, MapPin, Briefcase, Building, CreditCard, ShieldCheck, Heart } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export const MyProfilePage: React.FC = () => {
  const { fullName, email } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [phone, setPhone] = useState("+1 (555) 019-2834");
  const [address, setAddress] = useState("450 Mission Street, Suite 1200, San Francisco, CA");
  const [emergencyContact, setEmergencyContact] = useState("Jane Rivera (Spouse) - +1 (555) 902-1144");
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsEditing(false);
    setSaveMessage("Profile contact details updated successfully.");
    setTimeout(() => setSaveMessage(null), 3000);
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Top Profile Card */}
      <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 border border-brand-400/30 flex items-center justify-center text-white text-2xl font-bold shadow-xl shrink-0">
          {getInitials(fullName || "Alex Rivera")}
        </div>

        <div className="flex-1 text-center sm:text-left space-y-1">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <h1 className="text-2xl font-bold text-slate-100">{fullName || "Alex Rivera"}</h1>
            <Button
              variant={isEditing ? "ghost" : "primary"}
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
              className="text-xs"
            >
              {isEditing ? "Cancel" : "Edit Contact Details"}
            </Button>
          </div>
          <p className="text-xs text-brand-400 font-medium">Senior Full Stack Engineer &bull; Staff Grade</p>
          <div className="pt-2 flex flex-wrap justify-center sm:justify-start items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-slate-500" />
              {email || "arivera@vertexerp.io"}
            </span>
            <span className="flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-slate-500" />
              Engineering & Architecture
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              San Francisco, CA
            </span>
          </div>
        </div>
      </div>

      {saveMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs">
          {saveMessage}
        </div>
      )}

      {/* Details Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal & Contact Details */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <User className="w-4 h-4 text-brand-400" />
            <span>Personal & Contact Information</span>
          </h3>

          {isEditing ? (
            <form onSubmit={handleSave} className="space-y-3 text-xs">
              <Input label="Phone Number" value={phone} onChange={(e) => setPhone(e.target.value)} />
              <Input label="Residential Address" value={address} onChange={(e) => setAddress(e.target.value)} />
              <Input label="Emergency Contact & Relationship" value={emergencyContact} onChange={(e) => setEmergencyContact(e.target.value)} />
              <div className="pt-2 flex justify-end">
                <Button type="submit" variant="primary" size="sm" className="text-xs">
                  Save Changes
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500 text-[11px] block">Official Email</span>
                <span className="font-semibold text-slate-200">{email || "arivera@vertexerp.io"}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Primary Phone</span>
                <span className="font-semibold text-slate-200">{phone}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Residential Address</span>
                <span className="font-semibold text-slate-200">{address}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Emergency Contact</span>
                <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Heart className="w-3.5 h-3.5 text-rose-400" />
                  {emergencyContact}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Official Employment Details */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-emerald-400" />
            <span>Employment & Organization Record</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-500 text-[11px] block">Employee Number</span>
              <span className="font-semibold text-slate-200">EMP-00102</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Employment Status</span>
              <span className="font-semibold text-emerald-400">Full-Time Confirmed</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Date of Joining</span>
              <span className="font-semibold text-slate-200">January 15, 2024 (2 yrs, 10 mos)</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Reporting Manager</span>
              <span className="font-semibold text-slate-200">Sarah Connor (VP of Engineering)</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Work Shift</span>
              <span className="font-semibold text-slate-200">General Day Shift (09:00 - 18:00)</span>
            </div>
          </div>
        </div>

        {/* Bank & Remuneration Details */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-amber-400" />
            <span>Salary Account & Banking</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-500 text-[11px] block">Bank Name</span>
              <span className="font-semibold text-slate-200">JPMorgan Chase Bank, N.A.</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Account Number</span>
              <span className="font-semibold text-slate-200">••••••••4812</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Routing / IFSC Code</span>
              <span className="font-semibold text-slate-200">CHASUS33XXX</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Tax Identifier (SSN / PAN)</span>
              <span className="font-semibold text-slate-200">US-TAX-89274 (Verified)</span>
            </div>
          </div>
        </div>

        {/* Compliance & Verification Badge */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-purple-400" />
              <span>Identity & Security Status</span>
            </h3>
            <p className="mt-2 text-xs text-slate-400">
              Your organizational profile is authenticated through tenant-scoped Row-Level Security.
              All statutory documents have been validated by HR compliance.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Background Verification:</span>
              <span className="font-semibold text-emerald-400">COMPLETED</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Two-Factor Authentication:</span>
              <span className="font-semibold text-emerald-400">ENABLED</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Annual Compliance NDA:</span>
              <span className="font-semibold text-slate-200">Signed (2026)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
