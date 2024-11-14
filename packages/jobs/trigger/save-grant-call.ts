import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

type GrantCallResult = {
  id: string;
  title: string;
  description: string;
  organization: string;
  funding_amount: number;
  deadline: string;
  focus_areas: string[];
  eligibility_criteria: string[];
  requirements: string[];
  status: "open" | "closed" | "draft";
  meta?: Record<string, MetaData>;
};

type MetaData = {
  [key: string]: string | number | boolean | null | MetaData;
};

const grantCallSchema = z.object({
  id: z.string().optional(),
  title: z.string(),
  description: z.string(),
  organization: z.string(),
  funding_amount: z.number(),
  deadline: z.string(),
  focus_areas: z.array(z.string()),
  eligibility_criteria: z.array(z.string()),
  requirements: z.array(z.string()),
  status: z.enum(["open", "closed", "draft"]),
  meta: z.record(z.any()).optional(),
});

export const saveGrantCallTask = task({
  id: "save-grant-call",
  run: async (payload: z.infer<typeof grantCallSchema>, { ctx }) => {
    logger.info("Processing grant call");

    try {
      const { id, ...grantCallData } = payload;
      let result: GrantCallResult;

      if (id) {
        // Update existing grant call
        const { error } = await supabase
          .from("grant_calls")
          .update(grantCallData)
          .eq("id", id);

        if (error) throw error;
        result = { id, ...grantCallData };
      } else {
        // Insert new grant call
        const { data, error } = await supabase
          .from("grant_calls")
          .insert(grantCallData)
          .select()
          .single();

        if (error) throw error;
        result = data;
      }

      logger.info("Grant call saved successfully", { id: result.id });
      return { success: true, grantCall: result };
    } catch (error) {
      logger.error("Error saving grant call", { error, payload });
      return { success: false, error: (error as Error).message };
    }
  },
});
