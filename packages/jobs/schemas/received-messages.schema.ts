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

export const messageSchema = z.object({
  id: z.string(),
  _id: z.string(),
  from: z.string(),
  to: z.string(),
  userId: z.string(),
  data: z.object({
    text: z.string(),
  }),
  timestamp: z.number(),
  type: z.string(),
  isGroupChat: z.boolean(),
  chatId: z.string(),
  created: z.string(),
});

export type MessageResult = {
  id: string;
  user_id: string;
  text: string;
  timestamp: number;
  processed: boolean;
  meta: Record<string, unknown>;
  created_at: string;
};
