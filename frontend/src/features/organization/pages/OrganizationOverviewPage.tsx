import React from "react";
import { Link } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  Building2,
  GitFork,
  Users,
  Award,
  Layers,
  DollarSign,
  MapPin,
  Calendar,
  Sun,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import {
  useBranches,
  useDepartments,
  useTeams,
  useDesignations,
  useBusinessUnits,
  useCostCenters,
  useLocations,
  useCalendars,
  useHolidays,
} from "../api/queries";

export const OrganizationOverviewPage: React.FC = () => {
  const { data: branches, isLoading: lBranches } = useBranches();
  const { data: depts, isLoading: lDepts } = useDepartments();
  const { data: teams, isLoading: lTeams } = useTeams();
  const { data: desigs, isLoading: lDesigs } = useDesignations();
  const { data: bus, isLoading: lBus } = useBusinessUnits();
  const { data: costCenters, isLoading: lCostCenters } = useCostCenters();
  const { data: locations, isLoading: lLocations } = useLocations();
  const { data: calendars, isLoading: lCalendars } = useCalendars();
  const { data: holidays, isLoading: lHolidays } = useHolidays();

  const cards = [
    {
      title: "Branches",
      count: branches?.length ?? 0,
      description: "Physical operational offices and global HQs",
      to: "/organization/branches",
      icon: <Building2 className="w-5 h-5 text-brand-400" />,
      accent: "group-hover:border-brand-500/40",
      loading: lBranches,
    },
    {
      title: "Departments",
      count: depts?.length ?? 0,
      description: "Functional departments & tree hierarchies",
      to: "/organization/departments",
      icon: <GitFork className="w-5 h-5 text-amber-400" />,
      accent: "group-hover:border-amber-500/40",
      loading: lDepts,
    },
    {
      title: "Teams",
      count: teams?.length ?? 0,
      description: "Cross-functional project teams & rosters",
      to: "/organization/teams",
      icon: <Users className="w-5 h-5 text-emerald-400" />,
      accent: "group-hover:border-emerald-500/40",
      loading: lTeams,
    },
    {
      title: "Designations",
      count: desigs?.length ?? 0,
      description: "Job role titles and grade levels (1-10)",
      to: "/organization/designations",
      icon: <Award className="w-5 h-5 text-yellow-400" />,
      accent: "group-hover:border-yellow-500/40",
      loading: lDesigs,
    },
    {
      title: "Business Units",
      count: bus?.length ?? 0,
      description: "Strategic enterprise divisions and lines",
      to: "/organization/business-units",
      icon: <Layers className="w-5 h-5 text-fuchsia-400" />,
      accent: "group-hover:border-fuchsia-500/40",
      loading: lBus,
    },
    {
      title: "Cost Centers",
      count: costCenters?.length ?? 0,
      description: "Departmental budget tracking units",
      to: "/organization/cost-centers",
      icon: <DollarSign className="w-5 h-5 text-emerald-400" />,
      accent: "group-hover:border-emerald-500/40",
      loading: lCostCenters,
    },
    {
      title: "Locations",
      count: locations?.length ?? 0,
      description: "Warehouses, plants, and facility sites",
      to: "/organization/locations",
      icon: <MapPin className="w-5 h-5 text-rose-400" />,
      accent: "group-hover:border-rose-500/40",
      loading: lLocations,
    },
    {
      title: "Work Calendars",
      count: calendars?.length ?? 0,
      description: "Standard 40hr shifts and work schedules",
      to: "/organization/calendars",
      icon: <Calendar className="w-5 h-5 text-orange-400" />,
      accent: "group-hover:border-orange-500/40",
      loading: lCalendars,
    },
    {
      title: "Holidays",
      count: holidays?.length ?? 0,
      description: "National, regional, and company holidays",
      to: "/organization/holidays",
      icon: <Sun className="w-5 h-5 text-amber-300" />,
      accent: "group-hover:border-amber-400/40",
      loading: lHolidays,
    },
  ];

  const totalEntities =
    (branches?.length ?? 0) +
    (depts?.length ?? 0) +
    (teams?.length ?? 0) +
    (desigs?.length ?? 0) +
    (bus?.length ?? 0) +
    (costCenters?.length ?? 0) +
    (locations?.length ?? 0) +
    (calendars?.length ?? 0) +
    (holidays?.length ?? 0);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-zinc-900/75 border border-zinc-800 rounded-2xl p-6 backdrop-blur-xl">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-widest text-brand-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Enterprise Structural Directory
          </span>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">
            Organization Domain Hub
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Manage organizational hierarchy, global branches, cost centers, calendars, and statutory holidays.
          </p>
        </div>

        <div className="px-4 py-3 rounded-xl bg-zinc-950/80 border border-zinc-800 flex items-center gap-4">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-semibold">
              Active Units Configured
            </div>
            <div className="text-2xl font-extrabold text-brand-400">{totalEntities}</div>
          </div>
          <div className="h-8 w-[1px] bg-zinc-800" />
          <div className="text-xs text-emerald-400 font-semibold">All 9 Domains Live</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {cards.map((c) => (
          <Card
            key={c.title}
            className={`group bg-zinc-900/70 border-zinc-800 hover:bg-zinc-900/95 hover:-translate-y-0.5 transition-all duration-200 ${c.accent}`}
          >
            <CardHeader className="flex-row items-center justify-between pb-3 border-zinc-800/80">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-zinc-950 border border-zinc-800 group-hover:border-brand-500/30 transition-colors">
                  {c.icon}
                </div>
                <div>
                  <CardTitle className="text-zinc-100">{c.title}</CardTitle>
                  <CardDescription className="text-zinc-400">{c.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-4 flex items-end justify-between">
              <div>
                <div className="text-xs text-zinc-400 font-medium">Total Registered</div>
                {c.loading ? (
                  <Skeleton className="h-8 w-16 mt-1" />
                ) : (
                  <div className="text-2xl font-bold text-zinc-50">{c.count}</div>
                )}
              </div>
              <Link to={c.to}>
                <Button variant="outline" size="sm" className="gap-1.5 text-xs group-hover:border-brand-500/50 group-hover:text-brand-300">
                  Manage <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
