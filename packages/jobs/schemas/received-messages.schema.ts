import { z } from "zod";

export const querySchema = z
  .object({
    userId: z.string().optional(),
    limit: z.number().int().min(0).optional(),
    offset: z.number().int().min(0).optional(),
    fromTimestamp: z.number().min(0).optional(),
    toTimestamp: z.number().min(0).optional(),
  })
  .refine(
    (data) =>
      !data.fromTimestamp ||
      !data.toTimestamp ||
      data.toTimestamp >= data.fromTimestamp,
    { message: "toTimestamp must be greater than or equal to fromTimestamp" },
  );
