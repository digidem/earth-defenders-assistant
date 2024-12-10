import { swagger } from "@elysiajs/swagger";
import { Elysia } from "elysia";
import {
  handleGetMessages,
  handleHealthCheck,
  handleSendMessage,
} from "./routes";
import { messageSchema, queryParamsSchema } from "./types";

const app = new Elysia()
  .use(
    swagger({
      documentation: {
        info: {
          title: "Earth Defenders Assistant Messaging API",
          version: "1.0.0",
          description:
            "API for handling messaging across different platforms (WhatsApp, Telegram, Simulator)",
        },
        tags: [
          { name: "messages", description: "Message operations" },
          { name: "health", description: "Health check endpoints" },
        ],
      },
    }),
  )
  .post("/api/messages/send", handleSendMessage, {
    detail: {
      tags: ["messages"],
      description: "Send a new message",
      request: {
        body: {
          type: "object",
          properties: {
            userId: { type: "string", example: "user123" },
            text: { type: "string", example: "Hello world" },
            platform: {
              type: "string",
              enum: ["whatsapp", "telegram", "simulator"],
              example: "whatsapp",
            },
            meta: {
              type: "object",
              example: { priority: "high" },
              optional: true,
            },
          },
          required: ["userId", "text", "platform"],
        },
      },
      responses: {
        "200": {
          description: "Message sent successfully",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  id: { type: "string" },
                  userId: { type: "string" },
                  text: { type: "string" },
                  platform: { type: "string" },
                  timestamp: { type: "number" },
                },
              },
            },
          },
        },
        "400": {
          description: "Invalid request payload",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  error: { type: "string" },
                },
              },
            },
          },
        },
      },
    },
  })
  .get("/api/messages/receive", handleGetMessages, {
    detail: {
      tags: ["messages"],
      description: "Get received messages",
      query: {
        userId: { type: "string", optional: true },
        limit: { type: "number", optional: true },
        offset: { type: "number", optional: true },
        platform: {
          type: "string",
          enum: ["whatsapp", "telegram", "simulator"],
          optional: true,
        },
      },
      responses: {
        "200": {
          description: "Messages retrieved successfully",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  messages: {
                    type: "array",
                    items: {
                      type: "object",
                      properties: {
                        id: { type: "string" },
                        userId: { type: "string" },
                        text: { type: "string" },
                        platform: { type: "string" },
                        timestamp: { type: "number" },
                      },
                    },
                  },
                },
              },
            },
          },
        },
        "400": {
          description: "Invalid request parameters",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  error: { type: "string" },
                },
              },
            },
          },
        },
      },
    },
  })
  .get("/api/messages/health", handleHealthCheck, {
    detail: {
      tags: ["health"],
      description: "Check API health status",
      responses: {
        "200": {
          description: "Health check successful",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  status: { type: "string", example: "healthy" },
                },
              },
            },
          },
        },
      },
    },
  })
  .listen(3000);

const swaggerUrl = `http://${app.server?.hostname || "localhost"}:${
  app.server?.port
}/swagger`;

console.log(
  "🦊 Messaging API is running at",
  app.server?.hostname,
  "on port",
  app.server?.port,
  `\n📚 Swagger documentation available at ${swaggerUrl}`,
);
