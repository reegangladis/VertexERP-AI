import { z } from "zod";

export const branchSchema = z.object({
  code: z.string().min(1, "Branch code is required").max(32),
  name: z.string().min(1, "Branch name is required").max(128),
  address_line1: z.string().min(1, "Address line 1 is required").max(255),
  address_line2: z.string().max(255).optional().nullable(),
  city: z.string().min(1, "City is required").max(64),
  state: z.string().min(1, "State is required").max(64),
  postal_code: z.string().min(1, "Postal code is required").max(32),
  country: z.string().max(3).default("USA"),
  phone: z.string().max(32).optional().nullable(),
  email: z.string().email("Invalid email format").optional().or(z.literal("")),
  is_headquarters: z.boolean().default(false),
  is_active: z.boolean().default(true),
});

export const departmentSchema = z.object({
  code: z.string().min(1, "Department code is required").max(32),
  name: z.string().min(1, "Department name is required").max(128),
  description: z.string().optional().nullable(),
  parent_department_id: z.string().uuid("Invalid Parent UUID").optional().or(z.literal("")),
  is_active: z.boolean().default(true),
});

export const teamSchema = z.object({
  code: z.string().min(1, "Team code is required").max(32),
  name: z.string().min(1, "Team name is required").max(128),
  description: z.string().optional().nullable(),
  department_id: z.string().uuid("Invalid Department UUID").optional().or(z.literal("")),
  is_active: z.boolean().default(true),
});

export const designationSchema = z.object({
  code: z.string().min(1, "Designation code is required").max(32),
  name: z.string().min(1, "Designation title is required").max(128),
  description: z.string().optional().nullable(),
  level: z.coerce.number().min(1, "Level must be >= 1").max(100).default(1),
  is_active: z.boolean().default(true),
});

export const businessUnitSchema = z.object({
  code: z.string().min(1, "Business unit code is required").max(32),
  name: z.string().min(1, "Business unit name is required").max(128),
  description: z.string().optional().nullable(),
  is_active: z.boolean().default(true),
});

export const costCenterSchema = z.object({
  code: z.string().min(1, "Cost center code is required").max(32),
  name: z.string().min(1, "Cost center name is required").max(128),
  description: z.string().optional().nullable(),
  department_id: z.string().uuid("Invalid Department UUID").optional().or(z.literal("")),
  annual_budget: z.coerce.number().min(0, "Budget cannot be negative").default(0),
  currency: z.string().min(3).max(3).default("USD"),
  is_active: z.boolean().default(true),
});

export const locationSchema = z.object({
  code: z.string().min(1, "Location code is required").max(32),
  name: z.string().min(1, "Location name is required").max(128),
  location_type: z.enum(["OFFICE", "WAREHOUSE", "PLANT", "STORE", "DATACENTER"]).default("OFFICE"),
  address_line1: z.string().min(1, "Address line 1 is required").max(255),
  address_line2: z.string().max(255).optional().nullable(),
  city: z.string().min(1, "City is required").max(64),
  state: z.string().min(1, "State is required").max(64),
  postal_code: z.string().min(1, "Postal code is required").max(32),
  country: z.string().max(3).default("USA"),
  latitude: z.coerce.number().min(-90).max(90).optional().nullable(),
  longitude: z.coerce.number().min(-180).max(180).optional().nullable(),
  is_active: z.boolean().default(true),
});

export const workCalendarSchema = z.object({
  code: z.string().min(1, "Calendar code is required").max(32),
  name: z.string().min(1, "Calendar name is required").max(128),
  description: z.string().optional().nullable(),
  time_zone: z.string().min(1, "Timezone is required").default("UTC"),
  is_default: z.boolean().default(false),
  standard_hours_per_day: z.coerce.number().min(0).max(24).default(8),
  is_active: z.boolean().default(true),
});

export const holidaySchema = z.object({
  name: z.string().min(1, "Holiday name is required").max(128),
  holiday_date: z.string().min(10, "Date (YYYY-MM-DD) is required"),
  holiday_type: z.enum(["NATIONAL", "REGIONAL", "COMPANY", "OPTIONAL"]).default("NATIONAL"),
  is_recurring: z.boolean().default(false),
  description: z.string().optional().nullable(),
});
