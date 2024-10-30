import { logger, task } from "@trigger.dev/sdk/v3";
import { z } from "zod";
import { supabase } from "../lib/supabase";

const messageSchema = z.object({
  id: z.string(),
  _id: z.string(),
  from: z.string(),
  to: z.string(),
  userId: z.string(),
  data: z.object({
    text: z.string()
  }),
  timestamp: z.number(),
  type: z.string(),
  isGroupChat: z.boolean(),
  chatId: z.string(),
  created: z.string()
});

export const saveReceivedMessageTask = task({
  id: "save-received-message",
  run: async (payload: z.infer<typeof messageSchema>, { ctx }) => {
    logger.info('Processing message', { id: payload.id });
    const { id, userId, data, timestamp } = payload;

    try {
      const { error } = await supabase
        .from("received_messages")
        .insert({
          id,
          user_id: userId,
          text: data.text,
          timestamp,
          processed: false,
          meta: payload
        });

      if (error) {
        logger.error("Failed to save message", { error });
        return { success: false, error: error.message };
      }

      logger.info("Message saved successfully", { id });
      return { success: true, messageId: id };
    } catch (error) {
      logger.error("Error saving message", { error, payload });
      return { success: false, error: (error as Error).message };
    }
  },
});
