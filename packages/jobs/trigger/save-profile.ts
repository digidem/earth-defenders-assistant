import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const profileSchema = z.object({
  id: z.string().optional(),
  userId: z.string(),
  biome: z.string(),
  ethnicGroup: z.string(),
  territory: z.string(),
  community: z.string(),
  meta: z.record(z.any()).optional(),
});

type MetaData = {
  [key: string]: string | number | boolean | null | MetaData;
};

type ProfileResult = {
  id: string;
  user_id: string;
  biome: string;
  ethnic_group: string;
  territory: string;
  community: string;
  meta?: Record<string, MetaData>;
  created_at: string;
};

export const saveProfileTask = task({
  id: "save-profile",
  run: async (payload: z.infer<typeof profileSchema>, { ctx }) => {
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
      return { success: false, error: (error as Error).message };
    }
  },
});
