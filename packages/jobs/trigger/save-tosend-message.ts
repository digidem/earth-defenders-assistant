import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const messageSchema = z.object({
  userId: z.string(),
  text: z.string(),
  timestamp: z.number(),
  meta: z.record(z.any()),
});

export const saveTosendMessageTask = task({
  id: "save-tosend-message",
  run: async (payload: z.infer<typeof messageSchema>, { ctx }) => {
    logger.info("Processing tosend message");

    try {
      const { error } = await supabase.from("tosend_messages").insert({
        user_id: payload.userId,
        text: payload.text,
        timestamp: payload.timestamp,
        meta: payload.meta,
      });

      if (error) {
        logger.error("Failed to save tosend message", { error });
        return { success: false, error: error.message };
      }

      logger.info("Tosend message saved successfully");
      return { success: true };
    } catch (error) {
      logger.error("Error saving tosend message", { error, payload });
      return { success: false, error: (error as Error).message };
    }
  },
});
