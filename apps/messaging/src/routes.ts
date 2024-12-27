import { logger } from "@eda/logger";
import { createClient } from "@supabase/supabase-js";
import { messageSchema, queryParamsSchema } from "./types";

const supabase = createClient(
  "http://localhost:54321", // Local Supabase URL from config.toml
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // Get this from Supabase Studio
);

const AI_API_URL = process.env.AI_API_URL || "http://127.0.0.1:8083";

export async function handleSendMessage(req: Request) {
  try {
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
      formData.append("audio", payload.audio);
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

    logger.info("Message processed by AI API", {
      sessionId: payload.sessionId,
    });
    return Response.json(data);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to process message";
    logger.error("Error processing message", { error: message });
    return Response.json({ error: message }, { status: 400 });
  }
}

export async function handleGetMessages(req: Request) {
  try {
    const url = new URL(req.url);
    const params = queryParamsSchema.parse(
      Object.fromEntries(url.searchParams),
    );

    let query = supabase
      .from("received_messages")
      .select("*")
      .order("timestamp", { ascending: false });

    if (params.userId) {
      query = query.eq("user_id", params.userId);
    }
    if (params.limit) {
      query = query.limit(params.limit);
    }
    if (params.offset) {
      query = query.range(
        params.offset,
        params.offset + (params.limit || 10) - 1,
      );
    }
    if (params.platform) {
      query = query.eq("meta->platform", params.platform);
    }

    const { data, error } = await query;

    if (error) throw error;

    return Response.json({ messages: data });
  } catch (error) {
    logger.error("Error fetching messages", { error });
    return Response.json(
      { error: "Failed to fetch messages" },
      { status: 400 },
    );
  }
}

export function handleHealthCheck() {
  return Response.json({ status: "healthy" });
}
