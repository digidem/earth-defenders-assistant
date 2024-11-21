import { z } from "zod";

export const querySchema = z.object({
  userId: z.string().optional(),
  biome: z.string().optional(),
  ethnicGroup: z.string().optional(),
  territory: z.string().optional(),
  community: z.string().optional(),
  limit: z.number().int().min(0).optional(),
  offset: z.number().int().min(0).optional(),
});
