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
      loading: lBranches,
    },
    {
      title: "Departments",
      count: depts?.length ?? 0,
      description: "Functional departments & tree hierarchies",
      to: "/organization/departments",
      icon: <GitFork className="w-5 h-5 text-indigo-400" />,
      loading: lDepts,
    },
    {
      title: "Teams",
      count: teams?.length ?? 0,
      description: "Cross-functional project teams & rosters",
      to: "/organization/teams",
      icon: <Users className="w-5 h-5 text-sky-400" />,
      loading: lTeams,
    },
    {
      title: "Designations",
      count: desigs?.length ?? 0,
      description: "Job role titles and grade levels (1-10)",
      to: "/organization/designations",
      icon: <Award className="w-5 h-5 text-amber-400" />,
      loading: lDesigs,
    },
    {
      title: "Business Units",
      count: bus?.length ?? 0,
      description: "Strategic enterprise divisions and lines",
      to: "/organization/business-units",
      icon: <Layers className="w-5 h-5 text-purple-400" />,
      loading: lBus,
    },
    {
      title: "Cost Centers",
      count: costCenters?.length ?? 0,
      description: "Departmental budget tracking units",
      to: "/organization/cost-centers",
      icon: <DollarSign className="w-5 h-5 text-emerald-400" />,
      loading: lCostCenters,
    },
    {
      title: "Locations",
      count: locations?.length ?? 0,
      description: "Warehouses, plants, and facility sites",
      to: "/organization/locations",
      icon: <MapPin className="w-5 h-5 text-rose-400" />,
      loading: lLocations,
    },
    {
      title: "Work Calendars",
      count: calendars?.length ?? 0,
      description: "Standard 40hr shifts and work schedules",
      to: "/organization/calendars",
      icon: <Calendar className="w-5 h-5 text-cyan-400" />,
      loading: lCalendars,
    },
    {
      title: "Holidays",
      count: holidays?.length ?? 0,
      description: "National, regional, and company holidays",
      to: "/organization/holidays",
      icon: <Sun className="w-5 h-5 text-yellow-400" />,
      loading: lHolidays,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Organization Domain Hub</h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage organizational hierarchy, sites, departments, cost centers, calendars, and enterprise governance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {cards.map((c) => (
          <Card key={c.title} className="hover:border-slate-700 transition-all">
            <CardHeader className="flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                  {c.icon}
                </div>
                <div>
                  <CardTitle>{c.title}</CardTitle>
                  <CardDescription>{c.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-3 flex items-end justify-between">
              <div>
                <div className="text-xs text-slate-400 font-medium">Total Registered</div>
                {c.loading ? (
                  <Skeleton className="h-8 w-16 mt-1" />
                ) : (
                  <div className="text-2xl font-bold text-slate-100">{c.count}</div>
                )}
              </div>
              <Link to={c.to}>
                <Button variant="outline" size="sm" className="gap-1 text-xs">
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
