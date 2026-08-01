/**
 * AuthPages — Enterprise Authentication UI
 *
 * Pages: Login | Register | ForgotPassword | ResetPassword | VerifyEmail | SessionExpired | Unauthorized
 *
 * All pages call real backend API endpoints.
 * Uses AuthContext for token management.
 * Premium glassmorphism enterprise design.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  Building2,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  ArrowRight,
  Loader2,
  Globe,
  Phone,
  Key,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Alert } from '@/components/Alert';
import { PasswordStrengthMeter } from '@/components/PasswordStrengthMeter';
import { useNotification } from '@/hooks/useNotification';
import { useAuth } from '@/store/AuthContext';
import { apiClient } from '@/services/apiClient';

// ─────────────────────────────────────────
// Validation Schemas
// ─────────────────────────────────────────

const PASSWORD_RULES = z
  .string()
  .min(8, 'Minimum 8 characters')
  .refine((v) => /[A-Z]/.test(v), 'Must contain an uppercase letter')
  .refine((v) => /[a-z]/.test(v), 'Must contain a lowercase letter')
  .refine((v) => /[0-9]/.test(v), 'Must contain a number')
  .refine((v) => /[^A-Za-z0-9]/.test(v), 'Must contain a special character');

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

const registerSchema = z
  .object({
    first_name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    email: z.string().email('Enter a valid email address'),
    phone: z.string().optional(),
    password: PASSWORD_RULES,
    confirm_password: z.string().min(1, 'Please confirm your password'),
    org_name: z.string().min(1, 'Organization name is required'),
    org_slug: z
      .string()
      .min(2, 'Slug must be at least 2 characters')
      .regex(/^[a-z0-9-]+$/, 'Only lowercase letters, numbers, and dashes'),
    industry: z.string().optional(),
    company_size: z.string().optional(),
    country: z.string().optional(),
    timezone: z.string().optional(),
    acceptTerms: z.boolean().refine((v) => v === true, 'You must accept the terms'),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  });

const forgotSchema = z.object({
  email: z.string().email('Enter a valid email address'),
});

const resetSchema = z
  .object({
    password: PASSWORD_RULES,
    confirm_password: z.string().min(1, 'Please confirm your password'),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  });

// ─────────────────────────────────────────
// Utility: Show/Hide Password Toggle
// ─────────────────────────────────────────

function usePasswordVisibility() {
  const [visible, setVisible] = useState(false);
  const toggle = () => setVisible((v) => !v);
  const type = visible ? 'text' : 'password';
  const icon = visible ? (
    <EyeOff className="h-4 w-4 text-muted-foreground" />
  ) : (
    <Eye className="h-4 w-4 text-muted-foreground" />
  );
  return { visible, toggle, type, icon };
}

// ─────────────────────────────────────────
// 1. LOGIN
// ─────────────────────────────────────────

export function Login() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const pwdToggle = usePasswordVisibility();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      await login(data.email, data.password);
      addNotification('Welcome back! Login successful.', 'success');
      navigate('/analytics/executive');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-1">
        <h3 className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Enterprise Access Console
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Sign in to your VertexERP AI workspace
        </p>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* SSO Buttons */}
      <div className="grid grid-cols-2 gap-2">
        {['Microsoft Azure SSO', 'Okta IdP SSO'].map((label) => (
          <button
            key={label}
            type="button"
            title={`${label} (coming soon)`}
            className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 transition flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700 opacity-60 cursor-not-allowed"
          >
            {label}
          </button>
        ))}
      </div>

      <div className="relative flex py-1 items-center">
        <div className="flex-grow border-t border-slate-200 dark:border-slate-800" />
        <span className="flex-shrink mx-3 text-[10px] uppercase font-mono text-slate-400">
          or continue with email
        </span>
        <div className="flex-grow border-t border-slate-200 dark:border-slate-800" />
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Enterprise Email Address"
          type="email"
          placeholder="name@organization.com"
          error={errors.email?.message as string}
          {...register('email')}
        />

        <div className="relative">
          <Input
            label="Password"
            type={pwdToggle.type}
            placeholder="••••••••••••"
            error={errors.password?.message as string}
            {...register('password')}
          />
          <button
            type="button"
            onClick={pwdToggle.toggle}
            className="absolute right-3 top-8 p-1 hover:bg-secondary rounded"
          >
            {pwdToggle.icon}
          </button>
        </div>

        <div className="flex items-center justify-between text-xs pt-1">
          <label className="flex items-center gap-2 text-slate-500 cursor-pointer">
            <input
              type="checkbox"
              {...register('rememberMe')}
              className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span>Remember device</span>
          </label>
          <Link
            to="/auth/forgot-password"
            className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          variant="primary"
          type="submit"
          className="w-full py-2.5 rounded-xl font-bold shadow-md transition"
          isLoading={isLoading}
        >
          {!isLoading && <ShieldCheck className="h-4 w-4 mr-1.5" />}
          Sign In to Workspace
        </Button>
      </form>

      <div className="text-center text-xs text-slate-400">
        <span>New to VertexERP? </span>
        <Link to="/auth/register" className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline">
          Register Organization
        </Link>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 2. REGISTER
// ─────────────────────────────────────────

const INDUSTRIES = [
  'Technology', 'Finance & Banking', 'Healthcare', 'Manufacturing',
  'Retail & E-commerce', 'Education', 'Real Estate', 'Logistics',
  'Media & Entertainment', 'Government', 'Other',
];

const COMPANY_SIZES = [
  '1–10 employees', '11–50 employees', '51–200 employees',
  '201–500 employees', '501–1000 employees', '1000+ employees',
];

export function Register() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const { register: registerUser, getDefaultDashboardRoute } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [watchedPassword, setWatchedPassword] = useState('');
  const pwdToggle = usePasswordVisibility();
  const confirmPwdToggle = usePasswordVisibility();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({ resolver: zodResolver(registerSchema) });

  const passwordValue = watch('password', '');

  useEffect(() => {
    setWatchedPassword(passwordValue || '');
  }, [passwordValue]);

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.post('/api/v1/auth/register', {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone || undefined,
        password: data.password,
        org_name: data.org_name,
        org_slug: data.org_slug,
        industry: data.industry || undefined,
        company_size: data.company_size || undefined,
        country: data.country || undefined,
        timezone: data.timezone || undefined,
      });

      const respData = res.data?.data ?? res.data;
      if (respData?.verification_token) {
        setDevToken(respData.verification_token);
      }

      setSuccess(true);
      addNotification('Organization created! Please verify your email.', 'success');
    } catch (err: any) {
      setError(err.message || 'Registration failed — email or organization slug may already exist');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="text-center space-y-6 py-4">
        <div className="flex justify-center">
          <div className="p-4 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <CheckCircle2 className="h-10 w-10 text-emerald-500" />
          </div>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-foreground">Organization Created!</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Your enterprise environment is being provisioned. Please verify your email address to activate your account.
          </p>
        </div>
        {devToken && (
          <div className="border border-amber-500/30 bg-amber-500/5 rounded-lg p-4 text-left space-y-2">
            <p className="text-xs font-bold text-amber-500 uppercase tracking-wide">
              Dev Mode — Verification Token
            </p>
            <code className="block text-[10px] font-mono text-foreground bg-background border border-border px-2 py-1.5 rounded break-all">
              {devToken}
            </code>
            <button
              onClick={() => navigate(`/auth/verify-email?token=${devToken}`)}
              className="text-xs text-indigo-500 hover:underline font-semibold"
            >
              Click to verify now →
            </button>
          </div>
        )}
        <Link to="/auth/login">
          <Button variant="primary" className="w-full">
            Proceed to Login
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="text-center">
        <h3 className="text-lg font-bold text-foreground">Register Organization</h3>
        <p className="text-xs text-muted-foreground">Launch your secure enterprise workspace</p>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-h-[420px] overflow-y-auto pr-1.5">
        {/* Personal Info */}
        <div className="border border-border rounded-lg p-4 space-y-4 bg-secondary/5">
          <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wide">
            Administrator Details
          </p>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="First Name"
              placeholder="John"
              error={errors.first_name?.message as string}
              {...register('first_name')}
            />
            <Input
              label="Last Name"
              placeholder="Doe"
              error={errors.last_name?.message as string}
              {...register('last_name')}
            />
          </div>
          <Input
            label="Email Address"
            type="email"
            placeholder="john@company.com"
            error={errors.email?.message as string}
            {...register('email')}
          />
          <Input
            label="Phone (optional)"
            type="tel"
            placeholder="+1 555 000 0000"
            error={errors.phone?.message as string}
            {...register('phone')}
          />

          <div className="relative">
            <Input
              label="Password"
              type={pwdToggle.type}
              placeholder="••••••••"
              error={errors.password?.message as string}
              {...register('password')}
            />
            <button type="button" onClick={pwdToggle.toggle} className="absolute right-3 top-8 p-1 hover:bg-secondary rounded">
              {pwdToggle.icon}
            </button>
          </div>

          <PasswordStrengthMeter password={watchedPassword} />

          <div className="relative">
            <Input
              label="Confirm Password"
              type={confirmPwdToggle.type}
              placeholder="••••••••"
              error={errors.confirm_password?.message as string}
              {...register('confirm_password')}
            />
            <button type="button" onClick={confirmPwdToggle.toggle} className="absolute right-3 top-8 p-1 hover:bg-secondary rounded">
              {confirmPwdToggle.icon}
            </button>
          </div>
        </div>

        {/* Organization Info */}
        <div className="border border-border rounded-lg p-4 space-y-4 bg-secondary/5">
          <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wide">
            Organization Details
          </p>
          <Input
            label="Organization Name"
            placeholder="Acme Corporation"
            error={errors.org_name?.message as string}
            {...register('org_name')}
          />
          <Input
            label="Organization Slug"
            placeholder="acme-corp"
            error={errors.org_slug?.message as string}
            {...register('org_slug')}
          />

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Industry</label>
              <select
                {...register('industry')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Select industry</option>
                {INDUSTRIES.map((i) => <option key={i} value={i}>{i}</option>)}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Company Size</label>
              <select
                {...register('company_size')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Select size</option>
                {COMPANY_SIZES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Country"
              placeholder="United States"
              error={errors.country?.message as string}
              {...register('country')}
            />
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Timezone</label>
              <select
                {...register('timezone')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="UTC">UTC (GMT+0)</option>
                <option value="America/New_York">EST (GMT-5)</option>
                <option value="America/Chicago">CST (GMT-6)</option>
                <option value="America/Denver">MST (GMT-7)</option>
                <option value="America/Los_Angeles">PST (GMT-8)</option>
                <option value="Europe/London">BST (GMT+1)</option>
                <option value="Europe/Paris">CET (GMT+1)</option>
                <option value="Asia/Kolkata">IST (GMT+5:30)</option>
                <option value="Asia/Tokyo">JST (GMT+9)</option>
                <option value="Australia/Sydney">AEST (GMT+10)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Terms */}
        <label className="flex items-start gap-3 cursor-pointer group">
          <input
            type="checkbox"
            {...register('acceptTerms')}
            className="mt-0.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-xs text-muted-foreground leading-relaxed group-hover:text-foreground transition">
            I agree to the{' '}
            <a href="#" className="text-primary hover:underline">Terms of Service</a> and{' '}
            <a href="#" className="text-primary hover:underline">Privacy Policy</a>
          </span>
        </label>
        {errors.acceptTerms && (
          <p className="text-xs text-destructive">{errors.acceptTerms.message as string}</p>
        )}

        <Button variant="primary" type="submit" className="w-full" isLoading={isLoading}>
          {!isLoading && <Building2 className="h-4 w-4 mr-1.5" />}
          Create Workspace
        </Button>
      </form>

      <div className="text-center text-xs">
        <span className="text-muted-foreground">Already have an account? </span>
        <Link to="/auth/login" className="text-primary hover:underline font-semibold">
          Sign In
        </Link>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 3. FORGOT PASSWORD
// ─────────────────────────────────────────

export function ForgotPassword() {
  const { addNotification } = useNotification();
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devToken, setDevToken] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(forgotSchema),
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.post('/api/v1/auth/forgot-password', { email: data.email });
      const respData = res.data?.data ?? res.data;
      if (respData?.reset_token) setDevToken(respData.reset_token);
      setSuccess(true);
      addNotification('Recovery instructions dispatched', 'info');
    } catch (err: any) {
      setError(err.message || 'Failed to send recovery email');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-bold text-foreground">Recover Password</h3>
        <p className="text-xs text-muted-foreground">Retrieve your enterprise credentials</p>
      </div>

      {success ? (
        <div className="text-center space-y-4 py-4">
          <div className="flex justify-center">
            <div className="p-3 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <CheckCircle2 className="h-10 w-10 text-emerald-500" />
            </div>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            If this email is registered, password recovery instructions have been dispatched to your inbox.
          </p>
          {devToken && (
            <div className="border border-amber-500/30 bg-amber-500/5 rounded-lg p-3 text-left space-y-2">
              <p className="text-xs font-bold text-amber-500 uppercase">Dev Mode — Reset Token</p>
              <code className="block text-[10px] font-mono text-foreground bg-background border border-border px-2 py-1 rounded break-all">
                {devToken}
              </code>
              <Link
                to={`/auth/reset-password?token=${devToken}`}
                className="text-xs text-indigo-500 hover:underline font-semibold"
              >
                Click to reset password →
              </Link>
            </div>
          )}
          <Link to="/auth/login">
            <Button variant="outline" className="w-full mt-2">
              Return to Login
            </Button>
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && <Alert variant="danger">{error}</Alert>}
          <Input
            label="Registered Email Address"
            type="email"
            placeholder="name@organization.com"
            error={errors.email?.message as string}
            {...register('email')}
          />
          <Button variant="primary" type="submit" className="w-full" isLoading={isLoading}>
            {!isLoading && <Mail className="h-4 w-4 mr-1.5" />}
            Send Recovery Email
          </Button>
          <div className="text-center">
            <Link to="/auth/login" className="text-xs text-muted-foreground hover:text-foreground">
              ← Back to Login
            </Link>
          </div>
        </form>
      )}
    </div>
  );
}

// ─────────────────────────────────────────
// 4. RESET PASSWORD
// ─────────────────────────────────────────

export function ResetPassword() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [watchedPassword, setWatchedPassword] = useState('');
  const pwdToggle = usePasswordVisibility();
  const confirmPwdToggle = usePasswordVisibility();

  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: zodResolver(resetSchema),
  });

  const passwordValue = watch('password', '');
  useEffect(() => setWatchedPassword(passwordValue || ''), [passwordValue]);

  const onSubmit = async (data: any) => {
    if (!token) {
      setError('Invalid or missing reset token. Please request a new recovery email.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await apiClient.post('/api/v1/auth/reset-password', {
        token,
        new_password: data.password,
      });
      addNotification('Password reset successfully! You can now log in.', 'success');
      navigate('/auth/login');
    } catch (err: any) {
      setError(err.message || 'Password reset failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="text-center space-y-4 py-4">
        <AlertTriangle className="h-10 w-10 text-amber-500 mx-auto" />
        <p className="text-sm text-muted-foreground">
          No reset token provided. Please use the link from your recovery email.
        </p>
        <Link to="/auth/forgot-password">
          <Button variant="primary" className="w-full">Request New Recovery Link</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-bold text-foreground">Reset Password</h3>
        <p className="text-xs text-muted-foreground">Establish a new secure access key</p>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="relative">
          <Input
            label="New Password"
            type={pwdToggle.type}
            placeholder="••••••••"
            error={errors.password?.message as string}
            {...register('password')}
          />
          <button type="button" onClick={pwdToggle.toggle} className="absolute right-3 top-8 p-1 hover:bg-secondary rounded">
            {pwdToggle.icon}
          </button>
        </div>

        <PasswordStrengthMeter password={watchedPassword} />

        <div className="relative">
          <Input
            label="Confirm New Password"
            type={confirmPwdToggle.type}
            placeholder="••••••••"
            error={errors.confirm_password?.message as string}
            {...register('confirm_password')}
          />
          <button type="button" onClick={confirmPwdToggle.toggle} className="absolute right-3 top-8 p-1 hover:bg-secondary rounded">
            {confirmPwdToggle.icon}
          </button>
        </div>

        <Button variant="primary" type="submit" className="w-full" isLoading={isLoading}>
          {!isLoading && <Key className="h-4 w-4 mr-1.5" />}
          Update Password
        </Button>
      </form>
    </div>
  );
}

// ─────────────────────────────────────────
// 5. VERIFY EMAIL
// ─────────────────────────────────────────

export function VerifyEmail() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'no-token'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('no-token');
      return;
    }
    apiClient
      .post('/api/v1/auth/verify-email', { token })
      .then(() => setStatus('success'))
      .catch((err: any) => {
        setMessage(err.message || 'Verification failed');
        setStatus('error');
      });
  }, [token]);

  if (status === 'loading') {
    return (
      <div className="text-center space-y-4 py-8">
        <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
        <p className="text-sm text-muted-foreground">Verifying your email address…</p>
      </div>
    );
  }

  if (status === 'no-token') {
    return (
      <div className="text-center space-y-4 py-4">
        <AlertTriangle className="h-10 w-10 text-amber-500 mx-auto" />
        <p className="text-sm text-muted-foreground">
          No verification token provided. Please check your email for the verification link.
        </p>
        <Link to="/auth/login">
          <Button variant="outline" className="w-full">Go to Login</Button>
        </Link>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="text-center space-y-4 py-4">
        <AlertTriangle className="h-10 w-10 text-red-500 mx-auto" />
        <div className="space-y-1">
          <h3 className="font-bold text-foreground">Verification Failed</h3>
          <p className="text-sm text-muted-foreground">{message}</p>
        </div>
        <Link to="/auth/login">
          <Button variant="outline" className="w-full">Return to Login</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="text-center space-y-6 py-4">
      <div className="flex justify-center">
        <div className="p-4 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <CheckCircle2 className="h-10 w-10 text-emerald-500" />
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-foreground">Email Verified!</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Your account is now active and ready. Welcome to VertexERP AI.
        </p>
      </div>
      <Link to="/auth/login" className="block">
        <Button variant="primary" className="w-full">
          Sign In to Platform
          <ArrowRight className="h-4 w-4 ml-1.5" />
        </Button>
      </Link>
    </div>
  );
}

// ─────────────────────────────────────────
// 6. SESSION EXPIRED
// ─────────────────────────────────────────

export function SessionExpired() {
  return (
    <div className="text-center space-y-6 py-4">
      <div className="flex justify-center">
        <div className="p-4 rounded-full bg-amber-500/10 border border-amber-500/20">
          <AlertTriangle className="h-10 w-10 text-amber-500" />
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-foreground">Session Expired</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Your session has expired or was revoked. Please sign in again to continue.
        </p>
      </div>
      <Link to="/auth/login" className="block">
        <Button variant="primary" className="w-full">
          <RefreshCw className="h-4 w-4 mr-1.5" />
          Re-Authenticate
        </Button>
      </Link>
    </div>
  );
}

// ─────────────────────────────────────────
// 7. UNAUTHORIZED
// ─────────────────────────────────────────

export function Unauthorized() {
  const navigate = useNavigate();
  return (
    <div className="text-center space-y-6 py-4">
      <div className="flex justify-center">
        <div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
          <Lock className="h-10 w-10 text-red-500" />
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-foreground">Access Denied</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          You do not have the required permissions to access this resource. Contact your administrator.
        </p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" className="flex-1" onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Link to="/analytics/executive" className="flex-1">
          <Button variant="primary" className="w-full">Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
