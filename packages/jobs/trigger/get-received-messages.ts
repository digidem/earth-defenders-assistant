import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";
import type { querySchema } from "../schemas/received-messages.schema";

export const getReceivedMessagesTask = task({
  id: "get-received-messages",
  run: async (payload: z.infer<typeof querySchema>, { ctx }) => {
    logger.info("Fetching messages", { filters: payload });

    try {
      let query = supabase
        .from("received_messages")
        .select("*")
        .order("timestamp", { ascending: false });

      if (payload.userId) {
        query = query.eq("user_id", payload.userId);
      }

      if (payload.fromTimestamp) {
        query = query.gte("timestamp", payload.fromTimestamp);
      }

      if (payload.toTimestamp) {
        query = query.lte("timestamp", payload.toTimestamp);
      }

      if (payload.limit) {
        query = query.limit(payload.limit);
      }

      if (payload.offset) {
        query = query.range(
          payload.offset,
          payload.offset + (payload.limit || 50) - 1,
        );
      }

      const { data, error } = await query;

      if (error) {
        logger.error("Failed to fetch messages", { error });
        return { success: false, error: error.message };
      }

      logger.info("Messages fetched successfully", { count: data.length });
      return { success: true, messages: data };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error occurred";
      logger.error("Error fetching messages", { error: errorMessage });
      return { success: false, error: errorMessage };
    }
  },
});
