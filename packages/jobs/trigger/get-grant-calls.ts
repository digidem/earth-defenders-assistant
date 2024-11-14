import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const querySchema = z.object({
  userId: z.string().optional(),
  limit: z.number().optional(),
  offset: z.number().optional(),
  status: z.enum(["open", "closed", "draft"]).optional(),
  focusArea: z.string().optional(),
  minAmount: z.number().optional(),
  maxAmount: z.number().optional(),
});

export const getGrantCallsTask = task({
  id: "get-grant-calls",
  run: async (payload: z.infer<typeof querySchema>, { ctx }) => {
    logger.info("Fetching grant calls", { filters: payload });

    try {
      let query = supabase
        .from("grant_calls")
        .select("*")
        .order("created_at", { ascending: false });

      if (payload.status) {
        query = query.eq("status", payload.status);
      }

      if (payload.focusArea) {
        query = query.contains("focus_areas", [payload.focusArea]);
      }

      if (payload.minAmount) {
        query = query.gte("funding_amount", payload.minAmount);
      }

      if (payload.maxAmount) {
        query = query.lte("funding_amount", payload.maxAmount);
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
        logger.error("Failed to fetch grant calls", { error });
        return { success: false, error: error.message };
      }

      logger.info("Grant calls fetched successfully", { count: data.length });
      return { success: true, grantCalls: data };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error occurred";
      logger.error("Error fetching grant calls", { error: errorMessage });
      return { success: false, error: errorMessage };
    }
  },
});
