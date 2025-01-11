import { logger } from "@eda/logger";
import { createClient } from "@supabase/supabase-js";
import { messageSchema, queryParamsSchema } from "./types";

const supabase = createClient(
  "http://localhost:54321", // Local Supabase URL from config.toml
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // Get this from Supabase Studio
);

const AI_API_URL = process.env.AI_API_URL || "http://127.0.0.1:8083";

// Add new function to get/create Supabase ID
async function getSupabaseId(whatsappId: string): Promise<string> {
  try {
    // First check if user exists
    const { data: existingUser } = await supabase
      .from("messages")
      .select("id")
      .eq("whatsapp_id", whatsappId)
      .single();

    if (existingUser) {
      return existingUser.id;
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
  try {
    const payload = messageSchema.parse(req.body);

    // Get Supabase ID from WhatsApp ID
    const supabaseId = await getSupabaseId(payload.sessionId);

    logger.info("Processing message", {
      whatsappId: payload.sessionId,
      supabaseId,
      hasAudio: !!payload.audio,
    });

    const formData = new FormData();
    formData.append("message", payload.message);
    formData.append("session_id", supabaseId); // Use Supabase ID instead
    if (payload.platform) {
      formData.append("platform", payload.platform);
    }

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
      .eq("user_id", supabaseId) // Use Supabase ID
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
      supabaseId, // Use Supabase ID
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
