import { logger, task } from "@trigger.dev/sdk/v3";
import { supabase } from "../lib/supabase";

export const getGrantCallsTask = task({
  id: "get-grant-calls",
  run: async ({ status }: { status?: string }, { ctx }) => {
    logger.info("Fetching grant calls", { status });

    try {
      let query = supabase
        .from("grant_calls")
        .select("*")
        .order("created_at", { ascending: false });

      if (status) {
        query = query.eq("status", status);
      }

      const { data, error } = await query;

      if (error) {
        logger.error("Failed to fetch grant calls", { error });
        return { success: false, error: error.message };
      }

      logger.info("Grant calls fetched successfully");
      return { success: true, grantCalls: data };
    } catch (error) {
      logger.error("Error fetching grant calls", { error });
      return { success: false, error: (error as Error).message };
    }
  },
});
