import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const grantCallSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  deadline: z.string(),
  fundingAmount: z.number(),
  eligibility: z.string(),
  meta: z.record(z.any()).optional(),
});

export const saveGrantCallTask = task({
  id: "save-grant-call",
  run: async (payload: z.infer<typeof grantCallSchema>, { ctx }) => {
    logger.info("Saving grant call", { id: payload.id });

    try {
      const { error } = await supabase.from("grant_calls").insert({
        ...payload,
        created_at: new Date().toISOString(),
      });

      if (error) {
        logger.error("Failed to save grant call", { error });
        return { success: false, error: error.message };
      }

      logger.info("Grant call saved successfully", { id: payload.id });
      return { success: true, grantCallId: payload.id };
    } catch (error) {
      logger.error("Error saving grant call", { error, payload });
      return {
        success: false,
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  },
});
