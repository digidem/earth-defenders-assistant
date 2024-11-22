import { z } from "zod";

export const querySchema = z
  .object({
    userId: z.string().optional(),
    limit: z.number().int().min(0).optional(),
    offset: z.number().int().min(0).optional(),
    fromTimestamp: z.number().min(0).optional(),
    toTimestamp: z.number().min(0).optional(),
    processed: z.boolean().optional(),
  })
  .refine(
    (data) =>
      !data.fromTimestamp ||
      !data.toTimestamp ||
      data.toTimestamp >= data.fromTimestamp,
    { message: "toTimestamp must be greater than or equal to fromTimestamp" },
  );

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

const messageSchema = z.object({
  userId: z.string().min(1),
  text: z.string().min(1),
  timestamp: z.number(),
  meta: z.record(z.string(), metaValueSchema).optional(),
});

export type MetaValue =
  | string
  | number
  | boolean
  | null
  | Array<string | number | boolean | null>
  | Record<string, string | number | boolean | null>;

export { messageSchema };
