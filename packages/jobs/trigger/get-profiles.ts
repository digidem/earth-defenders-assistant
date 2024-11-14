import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const querySchema = z.object({
  userId: z.string().optional(),
  biome: z.string().optional(),
  ethnicGroup: z.string().optional(),
  territory: z.string().optional(),
  community: z.string().optional(),
  limit: z.number().optional(),
  offset: z.number().optional(),
});

export const getProfilesTask = task({
  id: "get-profiles",
  run: async (payload: z.infer<typeof querySchema>, { ctx }) => {
    logger.info("Fetching profiles", { filters: payload });

    try {
      let query = supabase
        .from("profiles")
        .select("*")
        .order("created_at", { ascending: false });

      if (payload.userId) {
        query = query.eq("user_id", payload.userId);
      }

      if (payload.biome) {
        query = query.eq("biome", payload.biome);
      }

      if (payload.ethnicGroup) {
        query = query.eq("ethnic_group", payload.ethnicGroup);
      }

      if (payload.territory) {
        query = query.eq("territory", payload.territory);
      }

      if (payload.community) {
        query = query.eq("community", payload.community);
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
        logger.error("Failed to fetch profiles", { error });
        return { success: false, error: error.message };
      }

      logger.info("Profiles fetched successfully", { count: data.length });
      return { success: true, profiles: data };
    } catch (error) {
      logger.error("Error fetching profiles", { error });
      return { success: false, error: (error as Error).message };
    }
  },
});
