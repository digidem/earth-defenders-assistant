import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";

export const getTosendMessagesTask = task({
  id: "get-tosend-messages",
  run: async ({ userId }: { userId: string }, { ctx }) => {
    logger.info("Fetching tosend messages", { userId });

    try {
      const { data, error } = await supabase
        .from("tosend_messages")
        .select("*")
        .eq("user_id", userId)
        .order("timestamp", { ascending: false });

      if (error) {
        logger.error("Failed to fetch tosend messages", { error });
        return { success: false, error: error.message };
      }

      logger.info("Tosend messages fetched successfully");
      return { success: true, messages: data };
    } catch (error) {
      logger.error("Error fetching tosend messages", { error });
      return { success: false, error: (error as Error).message };
    }
  },
});
