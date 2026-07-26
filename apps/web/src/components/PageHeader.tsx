import React from 'react';
import { Breadcrumb, BreadcrumbItem } from './Breadcrumb';

interface PageHeaderProps {
  title: string;
  description?: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
}

export function PageHeader({
  title,
  description,
  subtitle,
  breadcrumbs,
  actions,
}: PageHeaderProps) {
  const displayDescription = description || subtitle;
  return (
    <div className="flex flex-col gap-2 pb-6 border-b border-border mb-6">
      {breadcrumbs && <Breadcrumb items={breadcrumbs} />}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
          {displayDescription && (
            <p className="text-sm text-muted-foreground">{displayDescription}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}
export default PageHeader;
