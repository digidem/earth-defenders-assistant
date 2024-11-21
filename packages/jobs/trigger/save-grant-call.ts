import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";
import type {
  GrantCallResult,
  saveGrantCallSchema,
} from "../schemas/grant-calls.schema";

export const saveGrantCallTask = task({
  id: "save-grant-call",
  run: async (payload: z.infer<typeof saveGrantCallSchema>, { ctx }) => {
    logger.info("Processing grant call");

    try {
      const { id, ...grantCallData } = payload;
      let result: GrantCallResult;

      if (id) {
        // Update existing grant call
        const { data, error } = await supabase
          .from("grant_calls")
          .update(grantCallData)
          .eq("id", id)
          .select()
          .single();

        if (error) throw error;
        result = data;
      } else {
        // Insert new grant call
        const { data, error } = await supabase
          .from("grant_calls")
          .insert(grantCallData)
          .select()
          .single();

        if (error) throw error;
        result = data;
      }

      logger.info("Grant call saved successfully", { id: result.id });
      return { success: true, grantCall: result };
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
