import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { fetchVersion } from '@/services/api';
import {
  Terminal,
  Cpu,
  Layers,
  Database,
  Search,
  FileCode,
  Activity,
  ArrowRight,
} from 'lucide-react';

export function LandingPage() {
  const { data: apiVersion, status } = useQuery({
    queryKey: ['api-version'],
    queryFn: fetchVersion,
    retry: 1,
  });

  const features = [
    {
      icon: Cpu,
      title: 'Generative AI & Copilot',
      desc: 'Native AI chat capabilities, document query engines, and automated business workflows.',
    },
    {
      icon: Database,
      title: 'Enterprise ERP Foundation',
      desc: 'High-throughput modular architecture built for finance, CRM, HR, and manufacturing.',
    },
    {
      icon: Layers,
      title: 'Business Intelligence',
      desc: 'Aggregated reporting modules and analytics data cubes mapped directly to operations.',
    },
    {
      icon: Search,
      title: 'Enterprise Search',
      desc: 'Vector-driven hybrid search matching natural queries to database schemas and files.',
    },
    {
      icon: Activity,
      title: 'MLOps Platform',
      desc: 'Integrations for scheduling, retraining, and serving enterprise intelligence models.',
    },
    {
      icon: FileCode,
      title: 'Clean Core Architecture',
      desc: 'Strict domain-driven boundaries decoupling API schemas, services, and repositories.',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-16 py-8"
    >
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-4xl mx-auto py-12">
        <span className="px-3 py-1 text-xs font-mono uppercase tracking-widest text-muted-foreground border border-border rounded-full bg-secondary/30">
          Sprint 1.1: Foundations Complete
        </span>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          VertexERP <span className="text-muted-foreground font-light">AI</span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto font-light">
          Enterprise AI Operating System coordinating ERP logic, database migrations, structured
          logging, and distributed caching.
        </p>

        <div className="flex justify-center gap-4 pt-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-all select-none cursor-pointer"
          >
            Launch Core Console
            <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="/docs/Architecture.md"
            className="px-5 py-2.5 rounded border border-border bg-secondary/20 hover:bg-secondary/60 text-foreground font-medium text-sm transition-all select-none"
          >
            System Architecture
          </a>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feat, index) => (
          <div
            key={index}
            className="p-6 border border-border rounded bg-card hover:border-foreground/20 transition-all flex flex-col space-y-4"
          >
            <div className="p-2 border border-border bg-secondary/40 w-max rounded">
              <feat.icon className="h-5 w-5 text-foreground" />
            </div>
            <h3 className="font-semibold text-base">{feat.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{feat.desc}</p>
          </div>
        ))}
      </section>

      {/* Connected API Status Block */}
      <section className="border border-border rounded p-6 bg-secondary/10 max-w-2xl mx-auto space-y-4">
        <div className="flex items-center gap-3">
          <Terminal className="h-5 w-5 text-muted-foreground" />
          <h4 className="font-mono text-sm font-semibold uppercase tracking-wider">
            Connected API Status (FastAPI & Redis)
          </h4>
        </div>
        <div className="font-mono text-xs border border-border rounded bg-black p-4 text-emerald-400 overflow-x-auto space-y-1">
          {status === 'pending' && (
            <p className="animate-pulse text-yellow-400">&gt; Querying system configuration...</p>
          )}
          {status === 'error' && (
            <p className="text-red-400">
              &gt; Connection to backend failed. Please verify API is running.
            </p>
          )}
          {status === 'success' && apiVersion && (
            <>
              <p>&gt; Connection: Established</p>
              <p>&gt; Version: {apiVersion.version}</p>
              <p>&gt; Environment: {apiVersion.environment}</p>
              <p>&gt; Server Time: {new Date(apiVersion.timestamp).toLocaleString()}</p>
              <p>&gt; Core Status: {apiVersion.status.toUpperCase()}</p>
            </>
          )}
        </div>
      </section>
    </motion.div>
  );
}
export default LandingPage;
