import { logger, task } from "@trigger.dev/sdk/v3";
import type { z } from "zod";
import { supabase } from "../lib/supabase";

const profileSchema = z.object({
  userId: z.string(),
  fullName: z.string(),
  email: z.string().email(),
  organization: z.string().optional(),
  role: z.string().optional(),
  preferences: z.record(z.any()).optional(),
});

export const saveProfileTask = task({
  id: "save-profile",
  run: async (payload: z.infer<typeof profileSchema>, { ctx }) => {
    logger.info("Saving profile", { userId: payload.userId });

    try {
      const { error } = await supabase
        .from("profiles")
        .upsert({
          user_id: payload.userId,
          full_name: payload.fullName,
          email: payload.email,
          organization: payload.organization,
          role: payload.role,
          preferences: payload.preferences,
          updated_at: new Date().toISOString(),
        });

      if (error) {
        logger.error("Failed to save profile", { error });
        return { success: false, error: error.message };
      }

      logger.info("Profile saved successfully", { userId: payload.userId });
      return { success: true };
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
