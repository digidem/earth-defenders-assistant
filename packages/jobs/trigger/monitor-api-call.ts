import { task } from "@trigger.dev/sdk/v3";
import { logger } from "../../logger/src";
import type { ApiCall } from "../schemas/monitor-api-calls.schema";

export const monitorApiCallTask = task({
  id: "monitor-api-call",
  run: async (payload: ApiCall, { ctx }) => {
    logger.info("API Call monitored", {
      endpoint: payload.endpoint,
      statusCode: payload.statusCode,
      duration: payload.duration,
      sessionId: payload.sessionId,
    });

    try {
      // Here you could add logic to store metrics in your database
      // or send them to another monitoring service
      return {
        success: true,
        metrics: payload,
      };
    } catch (error) {
      logger.error("Error monitoring API call", { error, payload });
      return {
        success: false,
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  },
});
