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

// Query schema for getting profiles
export const querySchema = z.object({
  userId: z.string().optional(),
  biome: z.string().optional(),
  ethnicGroup: z.string().optional(),
  territory: z.string().optional(),
  community: z.string().optional(),
  limit: z.number().int().min(0).optional(),
  offset: z.number().int().min(0).optional(),
});

// Schema for saving profiles
export const saveProfileSchema = z.object({
  id: z.string().optional(),
  userId: z.string().min(1),
  biome: z.string().min(1),
  ethnicGroup: z.string().min(1),
  territory: z.string().min(1),
  community: z.string().min(1),
  meta: z.record(z.string(), metaValueSchema).optional(),
});

export type MetaValue =
  | string
  | number
  | boolean
  | null
  | Array<string | number | boolean | null>
  | Record<string, string | number | boolean | null>;

export type ProfileResult = {
  id: string;
  user_id: string;
  biome: string;
  ethnic_group: string;
  territory: string;
  community: string;
  meta?: Record<string, MetaValue>;
  created_at: string;
};
