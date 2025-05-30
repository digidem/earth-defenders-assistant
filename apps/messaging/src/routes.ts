import { config } from "@eda/config";
import { logger } from "@eda/logger";
import { createClient } from "@supabase/supabase-js";
import { configure, tasks } from "@trigger.dev/sdk/v3";
import { type Message, messageSchema, queryParamsSchema } from "./types";

// Replace Supabase client initialization
const supabase = createClient(
  config.databases.supabase.url,
  config.api_keys.supabase.service_key,
);

configure({
  secretKey: config.api_keys.trigger,
  baseURL: config.services.trigger.api_url,
});

// Replace AI API URL constant
const AI_API_URL = `http://localhost:${config.ports.ai_api}`;

// Add new function to get/create Supabase ID
async function getSupabaseId(whatsappId: string): Promise<string> {
  try {
    // First check if user exists
    const { data: existingUser } = await supabase
      .from("messages")
      .select("user_id")
      .eq("whatsapp_id", whatsappId)
      .single();

    if (existingUser) {
      return existingUser.user_id;
    }

    // If not exists, create new user
    const { data: newUser, error } = await supabase
      .from("messages")
      .insert([{ whatsapp_id: whatsappId }])
      .select("id")
      .single();

    if (error) throw error;
    return newUser.id;
  } catch (error) {
    logger.error("Error getting Supabase ID:", error);
    throw error;
  }
}

async function saveMessageToSupabase(
  userId: string,
  userMessage: string,
  aiResponse: string,
) {
  try {
    // First check if conversation exists
    const { data: existingConversation } = await supabase
      .from("messages")
      .select("conversation_history")
      .eq("user_id", userId)
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
        .eq("user_id", userId);
    } else {
      // Create new conversation
      const { error } = await supabase.from("messages").insert({
        user_id: userId,
        conversation_history: [
          {
            human: userMessage,
            ai: aiResponse,
            timestamp: new Date().toISOString(),
          },
        ],
      });
    }
  } catch (error) {
    logger.error("Error saving to Supabase:", error);
    throw error;
  }
}

// Modify handleSendMessage
export async function handleSendMessage(req: Request) {
  const startTime = performance.now();
  let payload: Message = {
    message: "",
    sessionId: "unknown",
  }; // Initialize with default values

  try {
    logger.info("Starting message processing", { body: req.body });

    payload = messageSchema.parse(req.body);
    logger.info("Payload parsed successfully", { payload });

    // Get Supabase ID from WhatsApp ID
    const supabaseId = await getSupabaseId(payload.sessionId);
    logger.info("Supabase ID retrieved", {
      supabaseId,
      whatsappId: payload.sessionId,
    });

    const formData = new FormData();
    formData.append("message", payload.message);
    formData.append("session_id", supabaseId);

    if (payload.platform) {
      formData.append("platform", payload.platform);
      logger.info("Platform added to formData", { platform: payload.platform });
    }

    if (payload.audio) {
      logger.info("Processing audio data", { hasAudio: true });
      try {
        const binaryStr = atob(payload.audio);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
          bytes[i] = binaryStr.charCodeAt(i);
        }
        const audioBlob = new Blob([bytes], { type: "audio/ogg" });
        formData.append("audio", audioBlob);
        logger.info("Audio data processed successfully");
      } catch (audioError) {
        logger.error("Error processing audio", { error: audioError });
        throw new Error("Failed to process audio data");
      }
    }

    // Log conversation history retrieval
    logger.info("Fetching conversation history", { userId: supabaseId });
    const { data: existingConversation, error: historyError } = await supabase
      .from("messages")
      .select("conversation_history")
      .eq("user_id", supabaseId)
      .single();

    if (historyError) {
      console.error(historyError);
      logger.error("Error fetching conversation history", {
        error: historyError,
      });
    }

    if (existingConversation?.conversation_history) {
      formData.append(
        "message_history",
        JSON.stringify(existingConversation.conversation_history),
      );
      logger.info("Conversation history added to formData", {
        historyLength: existingConversation.conversation_history.length,
      });
    }

    // Log API request - UPDATE THIS URL
    logger.info("Making API request to message handler", {
      url: `${AI_API_URL}/api/message_handler/handle`,
    });

    const response = await fetch(`${AI_API_URL}/api/message_handler/handle`, {
      method: "POST",
      headers: {
        accept: "application/json",
      },
      body: formData,
    });

    logger.info("API response received", {
      status: response.status,
      ok: response.ok,
    });

    const data = await response.json();
    console.log("API response parsed:", data);

    const duration = performance.now() - startTime;

    logger.info("Triggering monitor-api-call task");

    try {
      // Monitor API call using Trigger.dev
      await tasks.trigger("monitor-api-call", {
        endpoint: "/api/message_handler/handle",
        method: "POST",
        statusCode: response.status,
        duration,
        timestamp: new Date().toISOString(),
        sessionId: payload.sessionId,
      });
    } catch (triggerError) {
      logger.error("Error triggering monitoring task:", triggerError);
    }

    if (!response.ok) {
      throw new Error(data.message || "Failed to process message");
    }

    // Save message to Supabase after successful AI response
    await saveMessageToSupabase(
      supabaseId, // Use Supabase ID
      payload.message,
      data.result,
    );

    logger.info("Message processed and saved", {
      sessionId: payload.sessionId,
    });

    return Response.json(data);
  } catch (error) {
    const duration = performance.now() - startTime;

    try {
      // Monitor failed API calls
      await tasks.trigger("monitor-api-call", {
        endpoint: "/api/message_handler/handle",
        method: "POST",
        statusCode: 500,
        duration,
        timestamp: new Date().toISOString(),
        sessionId: payload.sessionId,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    } catch (triggerError) {
      logger.error(
        "Error triggering monitoring task for failed call:",
        triggerError,
      );
    }

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
