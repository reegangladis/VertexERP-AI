import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines Tailwind and conditional class names safely using clsx and tailwind-merge.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Formats monetary amounts with ISO currency codes and Decimal precision.
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = "USD"
): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return "$0.00";
  }
  const numericAmount = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numericAmount);
}

/**
 * Formats ISO date string to human-readable locale date (e.g., Nov 24, 2026).
 */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

/**
 * Formats ISO date-time string to readable timestamp.
 */
export function formatDateTime(dateTimeStr: string | null | undefined): string {
  if (!dateTimeStr) return "-";
  try {
    const d = new Date(dateTimeStr);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateTimeStr;
  }
}

/**
 * Generates uppercase user initials from a full name (e.g., "John Doe" -> "JD").
 */
export function getInitials(name: string | null | undefined): string {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
