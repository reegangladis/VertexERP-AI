import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Lock,
  Mail,
  User,
  Building,
  Key,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Alert } from '@/components/Alert';
import { useNotification } from '@/hooks/useNotification';

// Zod validation schemas
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

const registerSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .refine((val) => /[A-Z]/.test(val), 'Must contain at least one uppercase letter')
    .refine((val) => /[a-z]/.test(val), 'Must contain at least one lowercase letter')
    .refine((val) => /[0-9]/.test(val), 'Must contain at least one number')
    .refine((val) => /[^A-Za-z0-9]/.test(val), 'Must contain at least one symbol'),
  orgName: z.string().min(1, 'Organization name is required'),
  orgSlug: z
    .string()
    .min(2, 'Slug must be at least 2 characters')
    .regex(/^[a-z0-9-]+$/, 'Slug can only contain lowercase letters, numbers, and dashes'),
});

const forgotSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

const resetSchema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .refine((val) => /[A-Z]/.test(val), 'Must contain at least one uppercase letter')
    .refine((val) => /[a-z]/.test(val), 'Must contain at least one lowercase letter')
    .refine((val) => /[0-9]/.test(val), 'Must contain at least one number')
    .refine((val) => /[^A-Za-z0-9]/.test(val), 'Must contain at least one symbol'),
});

// 1. LOGIN SCREEN
export function Login() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      addNotification('Logged in successfully', 'success');
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
        <h3 className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Enterprise Access Console</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">Sign in to your VertexERP AI multi-tenant workspace</p>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Social SSO Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <button type="button" className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 transition flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700">
          <span>Microsoft Azure SSO</span>
        </button>
        <button type="button" className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 transition flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700">
          <span>Okta IdP SSO</span>
        </button>
      </div>

      <div className="relative flex py-1 items-center">
        <div className="flex-grow border-t border-slate-200 dark:border-slate-800"></div>
        <span className="flex-shrink mx-3 text-[10px] uppercase font-mono text-slate-400">or continue with email</span>
        <div className="flex-grow border-t border-slate-200 dark:border-slate-800"></div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Enterprise Email Address"
          type="email"
          placeholder="name@organization.com"
          error={errors.email?.message as string}
          {...register('email')}
        />
        <Input
          label="Password"
          type="password"
          placeholder="••••••••••••"
          error={errors.password?.message as string}
          {...register('password')}
        />

        <div className="flex items-center justify-between text-xs pt-1">
          <label className="flex items-center gap-2 text-slate-500 cursor-pointer">
            <input type="checkbox" className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" defaultChecked />
            <span>Remember device</span>
          </label>
          <Link to="/auth/forgot-password" className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline">
            Forgot password?
          </Link>
        </div>

        <Button variant="primary" type="submit" className="w-full py-2.5 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-700 shadow-md transition" isLoading={isLoading}>
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


// 2. REGISTER SCREEN
export function Register() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      addNotification('Organization created successfully. Verify your email to complete.', 'success');
      navigate('/auth/login');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-foreground">Create Tenant</h3>
        <p className="text-xs text-muted-foreground">Launch a secure isolated environment</p>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-h-[400px] overflow-y-auto pr-1">
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="First Name"
            placeholder="John"
            error={errors.firstName?.message as string}
            {...register('firstName')}
          />
          <Input
            label="Last Name"
            placeholder="Doe"
            error={errors.lastName?.message as string}
            {...register('lastName')}
          />
        </div>

        <Input
          label="Username"
          placeholder="johndoe"
          error={errors.username?.message as string}
          {...register('username')}
        />

        <Input
          label="Email Address"
          type="email"
          placeholder="john@company.com"
          error={errors.email?.message as string}
          {...register('email')}
        />

        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          error={errors.password?.message as string}
          {...register('password')}
        />

        <div className="border-t border-border pt-4 mt-2 space-y-4">
          <Input
            label="Organization Name"
            placeholder="Acme Corp"
            error={errors.orgName?.message as string}
            {...register('orgName')}
          />
          <Input
            label="Organization Slug"
            placeholder="acme-corp"
            error={errors.orgSlug?.message as string}
            {...register('orgSlug')}
          />
        </div>

        <Button variant="primary" type="submit" className="w-full mt-4" isLoading={isLoading}>
          Create Workspace
        </Button>
      </form>

      <div className="text-center text-xs">
        <span className="text-muted-foreground">Already have an organization? </span>
        <Link to="/auth/login" className="text-primary hover:underline">
          Sign In
        </Link>
      </div>
    </div>
  );
}

// 3. FORGOT PASSWORD SCREEN
export function ForgotPassword() {
  const { addNotification } = useNotification();
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotSchema),
  });

  const onSubmit = () => {
    setSuccess(true);
    addNotification('Password recovery instructions sent to email', 'info');
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-foreground">Recover Password</h3>
        <p className="text-xs text-muted-foreground">Retrieve your enterprise credentials</p>
      </div>

      {success ? (
        <div className="text-center space-y-4 py-4">
          <div className="flex justify-center text-emerald-500">
            <CheckCircle className="h-12 w-12" />
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            We have dispatched password recovery guidelines. Please check your inbox.
          </p>
          <Link to="/auth/login">
            <Button variant="outline" className="w-full mt-4">
              Return to Login
            </Button>
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Registered Email"
            type="email"
            placeholder="name@organization.com"
            error={errors.email?.message as string}
            {...register('email')}
          />
          <Button variant="primary" type="submit" className="w-full">
            Send Recovery Email
          </Button>
        </form>
      )}
    </div>
  );
}

// 4. RESET PASSWORD SCREEN
export function ResetPassword() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetSchema),
  });

  const onSubmit = () => {
    addNotification('Password updated successfully. You can now login.', 'success');
    navigate('/auth/login');
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-foreground">Reset Password</h3>
        <p className="text-xs text-muted-foreground">Establish a new secure access key</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="New Password"
          type="password"
          placeholder="••••••••"
          error={errors.password?.message as string}
          {...register('password')}
        />
        <Button variant="primary" type="submit" className="w-full">
          Update Credentials
        </Button>
      </form>
    </div>
  );
}

// 5. VERIFY EMAIL SCREEN
export function VerifyEmail() {
  return (
    <div className="text-center space-y-6 py-4">
      <div className="flex justify-center text-emerald-500">
        <CheckCircle className="h-12 w-12" />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-foreground">Email Verified</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Your user profile verification is complete. Your enterprise environment is active.
        </p>
      </div>
      <Link to="/auth/login" className="block">
        <Button variant="primary" className="w-full">
          Sign In to Platform
        </Button>
      </Link>
    </div>
  );
}

// 6. SESSION EXPIRED SCREEN
export function SessionExpired() {
  return (
    <div className="text-center space-y-6 py-4">
      <div className="flex justify-center text-amber-500">
        <AlertTriangle className="h-12 w-12" />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-foreground">Session Terminated</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Your active authorization token has expired or was revoked. Please log in again to resume work.
        </p>
      </div>
      <Link to="/auth/login" className="block">
        <Button variant="primary" className="w-full">
          Re-Authenticate
        </Button>
      </Link>
    </div>
  );
}
