import { logger } from "@eda/logger";
import { createClient } from "@supabase/supabase-js";
import { messageSchema, queryParamsSchema } from "./types";

const supabase = createClient(
  "http://localhost:54321", // Local Supabase URL from config.toml
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // Get this from Supabase Studio
);

const AI_API_URL = process.env.AI_API_URL || "http://127.0.0.1:8083";

async function saveMessageToSupabase(
  whatsappId: string,
  userMessage: string,
  aiResponse: string,
) {
  try {
    // First check if conversation exists
    const { data: existingConversation } = await supabase
      .from("messages")
      .select("conversation_history")
      .eq("whatsapp_id", whatsappId)
      .single();

    if (existingConversation) {
      // Update existing conversation
      const currentHistory = existingConversation.conversation_history || [];
      const updatedHistory = [
        ...currentHistory,
        {
          human: userMessage,
          ai: aiResponse,
          timestamp: new Date().toISOString(),
        },
      ];

      const { error } = await supabase
        .from("messages")
        .update({ conversation_history: updatedHistory })
        .eq("whatsapp_id", whatsappId);

      if (error) throw error;
    } else {
      // Create new conversation
      const { error } = await supabase.from("messages").insert({
        whatsapp_id: whatsappId,
        conversation_history: [
          {
            human: userMessage,
            ai: aiResponse,
            timestamp: new Date().toISOString(),
          },
        ],
      });

      if (error) throw error;
    }
  } catch (error) {
    logger.error("Error saving to Supabase:", error);
    throw error;
  }
}

export async function handleSendMessage(req: Request) {
  try {
    logger.info("Received message request");
    // Access body directly from Elysia's parsed request
    const payload = messageSchema.parse(req.body);

    logger.info("Received message request", {
      sessionId: payload.sessionId,
      hasAudio: !!payload.audio,
    });

    // Create FormData for AI API
    const formData = new FormData();
    formData.append("message", payload.message);
    formData.append("session_id", payload.sessionId);

    if (payload.audio) {
      const binaryStr = atob(payload.audio);
      const bytes = new Uint8Array(binaryStr.length);
      for (let i = 0; i < binaryStr.length; i++) {
        bytes[i] = binaryStr.charCodeAt(i);
      }
      const audioBlob = new Blob([bytes], { type: "audio/ogg" }); // Adjust mime type as needed
      formData.append("audio", audioBlob);
    }

    // Add message history to formData
    const { data: existingConversation } = await supabase
      .from("messages")
      .select("conversation_history")
      .eq("whatsapp_id", payload.sessionId)
      .single();

    if (existingConversation?.conversation_history) {
      formData.append(
        "message_history",
        JSON.stringify(existingConversation.conversation_history),
      );
    }

    // Forward request to AI API
    const response = await fetch(`${AI_API_URL}/api/classifier/classify`, {
      method: "POST",
      headers: {
        accept: "application/json",
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to process message");
    }

    // Save message to Supabase after successful AI response
    await saveMessageToSupabase(
      payload.sessionId,
      payload.message,
      data.result,
    );

    logger.info("Message processed and saved", {
      sessionId: payload.sessionId,
    });

    return Response.json(data);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to process message";
    logger.error("Error processing message", { error: message });
    console.error(error);
    return Response.json({ error: message }, { status: 400 });
  }
}

export function handleHealthCheck() {
  return Response.json({ status: "healthy" });
}
