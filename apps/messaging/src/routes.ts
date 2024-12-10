import { logger } from "@eda/logger";
import { createClient } from "@supabase/supabase-js";
import { messageSchema, queryParamsSchema } from "./types";

const supabase = createClient(
  "http://localhost:54321", // Local Supabase URL from config.toml
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // Get this from Supabase Studio
);

export async function handleSendMessage(req: Request) {
  try {
    const payload = messageSchema.parse(await req.json());

    const { data, error } = await supabase
      .from("tosend_messages")
      .insert([
        {
          user_id: payload.userId,
          text: payload.text,
          timestamp: Date.now(),
          meta: {
            platform: payload.platform,
            ...payload.meta,
          },
        },
      ])
      .select()
      .single();

    if (error) throw error;

    logger.info("Message queued for sending", { userId: payload.userId });
    return Response.json(data);
  } catch (error) {
    logger.error("Error queueing message", { error });
    return Response.json({ error: "Failed to queue message" }, { status: 400 });
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
