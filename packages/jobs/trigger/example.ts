import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";

const helloWorldSchema = z.string();

export const helloWorldTask = task({
  id: "hello-world",
  run: async (payload: z.infer<typeof helloWorldSchema>, { ctx }) => {
    logger.info("Running hello world task", { name: payload });

    try {
      return {
        success: true,
        message: `Hello ${payload}!`,
      };
    } catch (error) {
      logger.error("Error in hello world task", { error });
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});
