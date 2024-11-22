import { logger, task } from "@trigger.dev/sdk/v3";
import { supabase } from "../lib/supabase";

export const getProfilesTask = task({
  id: "get-profiles",
  run: async ({ userId }: { userId?: string }, { ctx }) => {
    logger.info("Fetching profiles", { userId });

    try {
      let query = supabase
        .from("profiles")
        .select("*");

      if (userId) {
        query = query.eq("user_id", userId);
      }

      const { data, error } = await query;

      if (error) {
        logger.error("Failed to fetch profiles", { error });
        return { success: false, error: error.message };
      }

      logger.info("Profiles fetched successfully");
      return { success: true, profiles: data };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error occurred";
      logger.error("Error fetching profiles", { error: errorMessage });
      return { success: false, error: errorMessage };
    }
  },
});
