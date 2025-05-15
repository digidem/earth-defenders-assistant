import { config } from "@eda/config";
import { swagger } from "@elysiajs/swagger";
import { Elysia } from "elysia";
import { handleHealthCheck, handleSendMessage } from "./routes";
import { messageSchema } from "./types";

const PORT = config.ports.messaging;
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
      description: "Process a message through AI API",
      requestBody: {
        content: {
          "application/json": {
            schema: {
              type: "object",
              properties: {
                message: { type: "string", example: "Hello world" },
                sessionId: { type: "string", example: "5515991306053" },
                audio: { type: "string", format: "binary", nullable: true },
              },
              required: ["message", "sessionId"],
            },
          },
        },
      },
      responses: {
        "200": {
          description: "Message processed successfully",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  result: { type: "string" },
                  session_id: { type: "string" },
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
  .listen(PORT);

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
