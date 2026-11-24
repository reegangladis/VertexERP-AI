import React from "react";
import { Badge } from "./Badge";

export interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const normalized = status ? status.toUpperCase().trim() : "UNKNOWN";

  let variant: "success" | "warning" | "danger" | "info" | "neutral" = "neutral";
  let label = status;

  switch (normalized) {
    // General approval / positive
    case "APPROVED":
    case "ACTIVE":
    case "COMPLETED":
    case "PRESENT":
    case "P":
    case "PAID":
    case "WON":
    case "CLOSED WON":
    case "QUALIFIED":
    case "SUCCESS":
      variant = "success";
      break;

    // Warning / pending review
    case "PENDING":
    case "IN_REVIEW":
    case "SUBMITTED":
    case "PROBATION":
    case "CONTACTED":
    case "NEGOTIATION":
    case "PROPOSAL":
    case "ON_DUTY":
    case "OD":
    case "WARM":
      variant = "warning";
      break;

    // Negative / blocked / rejected
    case "REJECTED":
    case "CANCELLED":
    case "FAILED":
    case "TERMINATED":
    case "ABSENT":
    case "A":
    case "DEAD":
    case "LOST":
    case "CLOSED LOST":
    case "DISQUALIFIED":
    case "OVERDUE":
      variant = "danger";
      break;

    // Informational / scheduled / leave
    case "LEAVE":
    case "L":
    case "HOLIDAY":
    case "H":
    case "NEW":
    case "OPEN":
    case "SCHEDULED":
    case "PROSPECTING":
    case "DRAFT":
    case "HOT":
      variant = "info";
      break;

    default:
      variant = "neutral";
      break;
  }

  return (
    <Badge variant={variant} className={className}>
      {label}
    </Badge>
  );
};
