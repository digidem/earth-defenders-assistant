import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";
import type {
  ProfileResult,
  saveProfileSchema,
} from "../schemas/profiles.schema";

export const saveProfileTask = task({
  id: "save-profile",
  run: async (payload: z.infer<typeof saveProfileSchema>, { ctx }) => {
    logger.info("Processing profile", { userId: payload.userId });

    try {
      const profileData = {
        user_id: payload.userId,
        biome: payload.biome,
        ethnic_group: payload.ethnicGroup,
        territory: payload.territory,
        community: payload.community,
        meta: payload.meta || {},
      };

      let result: ProfileResult;

      if (payload.id) {
        // Update existing profile
        const { data, error } = await supabase
          .from("profiles")
          .update(profileData)
          .eq("id", payload.id)
          .select()
          .single();

        if (error) throw error;
        result = data;
      } else {
        // Insert new profile
        const { data, error } = await supabase
          .from("profiles")
          .insert(profileData)
          .select()
          .single();

        if (error) throw error;
        result = data;
      }

      logger.info("Profile saved successfully", { id: result.id });
      return { success: true, profile: result };
    } catch (error) {
      logger.error("Error saving profile", { error, payload });
      return {
        success: false,
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  },
});
