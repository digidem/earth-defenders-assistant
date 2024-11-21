import { z } from "zod";

// Define specific types for meta values
const metaValueSchema = z.union([
  z.string(),
  z.number(),
  z.boolean(),
  z.null(),
  z.array(z.union([z.string(), z.number(), z.boolean(), z.null()])),
  z.record(
    z.string(),
    z.union([z.string(), z.number(), z.boolean(), z.null()]),
  ),
]);

export const querySchema = z
  .object({
    userId: z.string().optional(),
    limit: z.number().int().min(0).optional(),
    offset: z.number().int().min(0).optional(),
    status: z.enum(["open", "closed", "draft"]).optional(),
    focusArea: z.string().optional(),
    minAmount: z.number().min(0).optional(),
    maxAmount: z.number().min(0).optional(),
  })
  .refine(
    (data) =>
      !data.minAmount || !data.maxAmount || data.maxAmount >= data.minAmount,
    { message: "maxAmount must be greater than or equal to minAmount" },
  );

export const saveGrantCallSchema = z.object({
  id: z.string().optional(),
  title: z.string(),
  description: z.string(),
  organization: z.string(),
  funding_amount: z.number().min(0),
  deadline: z.string(),
  focus_areas: z.array(z.string()),
  eligibility_criteria: z.array(z.string()),
  requirements: z.array(z.string()),
  status: z.enum(["open", "closed", "draft"]),
  meta: z.record(z.string(), metaValueSchema).optional(),
});

export type MetaValue =
  | string
  | number
  | boolean
  | null
  | Array<string | number | boolean | null>
  | Record<string, string | number | boolean | null>;

export type GrantCallResult = {
  id: string;
  title: string;
  description: string;
  organization: string;
  funding_amount: number;
  deadline: string;
  focus_areas: string[];
  eligibility_criteria: string[];
  requirements: string[];
  status: "open" | "closed" | "draft";
  meta?: Record<string, MetaValue>;
};
