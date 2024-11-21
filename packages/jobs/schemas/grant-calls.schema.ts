import { z } from "zod";

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
