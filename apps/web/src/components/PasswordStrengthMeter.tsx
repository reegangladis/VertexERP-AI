/**
 * PasswordStrengthMeter — Real-time password strength indicator.
 * Evaluates: length, uppercase, lowercase, digit, special character.
 */

import React from 'react';

interface Rule {
  label: string;
  test: (v: string) => boolean;
}

const RULES: Rule[] = [
  { label: 'At least 8 characters', test: (v) => v.length >= 8 },
  { label: 'Uppercase letter (A–Z)', test: (v) => /[A-Z]/.test(v) },
  { label: 'Lowercase letter (a–z)', test: (v) => /[a-z]/.test(v) },
  { label: 'Number (0–9)', test: (v) => /[0-9]/.test(v) },
  { label: 'Special character (!@#…)', test: (v) => /[^A-Za-z0-9]/.test(v) },
];

type Strength = 'empty' | 'weak' | 'fair' | 'good' | 'strong';

function getStrength(password: string): Strength {
  if (!password) return 'empty';
  const passed = RULES.filter((r) => r.test(password)).length;
  if (passed <= 1) return 'weak';
  if (passed === 2) return 'fair';
  if (passed === 3 || passed === 4) return 'good';
  return 'strong';
}

const STRENGTH_META: Record<Strength, { label: string; color: string; bars: number }> = {
  empty: { label: '', color: 'bg-border', bars: 0 },
  weak: { label: 'Weak', color: 'bg-red-500', bars: 1 },
  fair: { label: 'Fair', color: 'bg-amber-500', bars: 2 },
  good: { label: 'Good', color: 'bg-blue-500', bars: 3 },
  strong: { label: 'Strong', color: 'bg-emerald-500', bars: 4 },
};

interface Props {
  password: string;
  className?: string;
}

export function PasswordStrengthMeter({ password, className = '' }: Props) {
  const strength = getStrength(password);
  const meta = STRENGTH_META[strength];

  if (!password) return null;

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Strength bars */}
      <div className="flex items-center gap-1.5">
        {[1, 2, 3, 4].map((bar) => (
          <div
            key={bar}
            className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
              bar <= meta.bars ? meta.color : 'bg-border'
            }`}
          />
        ))}
        {strength !== 'empty' && (
          <span
            className={`text-[10px] font-bold ml-1 uppercase tracking-wide transition-colors ${
              strength === 'weak'
                ? 'text-red-500'
                : strength === 'fair'
                  ? 'text-amber-500'
                  : strength === 'good'
                    ? 'text-blue-500'
                    : 'text-emerald-500'
            }`}
          >
            {meta.label}
          </span>
        )}
      </div>

      {/* Rules checklist */}
      <ul className="space-y-0.5">
        {RULES.map((rule) => {
          const passed = rule.test(password);
          return (
            <li
              key={rule.label}
              className={`flex items-center gap-1.5 text-[11px] transition-colors ${
                passed ? 'text-emerald-500' : 'text-muted-foreground'
              }`}
            >
              <div
                className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center flex-shrink-0 transition-all ${
                  passed
                    ? 'bg-emerald-500 border-emerald-500'
                    : 'border-border'
                }`}
              >
                {passed && (
                  <svg
                    viewBox="0 0 12 12"
                    className="w-2 h-2 text-white fill-current"
                  >
                    <path d="M10 3L5 8L2 5" stroke="white" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              {rule.label}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default PasswordStrengthMeter;
