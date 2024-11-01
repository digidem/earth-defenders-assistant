import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";

export const getReceivedMessagesTask = task({
  id: "get-received-messages",
  run: async ({ userId }: { userId: string }, { ctx }) => {
    logger.info("Fetching received messages", { userId });

    try {
      const { data, error } = await supabase
        .from("received_messages")
        .select("*")
        .eq("user_id", userId)
        .order("timestamp", { ascending: false });

      if (error) {
        logger.error("Failed to fetch received messages", { error });
        return { success: false, error: error.message };
      }

      logger.info("Received messages fetched successfully");
      return { success: true, messages: data };
    } catch (error) {
      logger.error("Error fetching received messages", { error });
      return { success: false, error: (error as Error).message };
    }
  },
});
