import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";
import type { querySchema } from "../schemas/tosend-messages.schema";

export const getTosendMessagesTask = task({
  id: "get-tosend-messages",
  run: async (payload: z.infer<typeof querySchema>, { ctx }) => {
    logger.info("Fetching tosend messages", { filters: payload });

    try {
      let query = supabase
        .from("tosend_messages")
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

      if (payload.processed !== undefined) {
        query = query.eq("processed", payload.processed);
      }

      const { data, error } = await query;

      if (error) {
        logger.error("Failed to fetch tosend messages", { error });
        return { success: false, error: error.message };
      }

      logger.info("Tosend messages fetched successfully", {
        count: data.length,
      });
      return { success: true, messages: data };
    } catch (error) {
      logger.error("Error fetching tosend messages", { error });
      return { success: false, error: (error as Error).message };
    }
  },
});
