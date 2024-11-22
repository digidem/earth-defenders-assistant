import { describe, expect, it } from "vitest";
import { messageSchema } from "../schemas/tosend-messages.schema";

interface MessageParams {
  userId: string;
  text: string;
  timestamp: number;
  meta?: Record<string, unknown>;
}

// Test factories
function createValidMessage(overrides?: Partial<MessageParams>): MessageParams {
  return {
    userId: "user123",
    text: "Hello, this is a test message",
    timestamp: Date.now(),
    ...overrides,
  };
}

describe("Save Tosend Message Schema Validation", () => {
  describe("valid messages", () => {
    it("should parse a complete valid message", () => {
      const validMessage = createValidMessage();
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });

    it("should accept messages with meta data", () => {
      const validMessage = createValidMessage({
        meta: {
          priority: "high",
          category: "notification",
          tags: ["important", "urgent"],
        },
      });
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });

    it("should accept valid timestamps", () => {
      const validMessage = createValidMessage({
        timestamp: 1234567890,
      });
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });
  });

  describe("invalid messages", () => {
    it("should throw an error for missing required fields", () => {
      const invalidMessage = {
        userId: "user123",
        // Missing other required fields
      };

      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for empty text", () => {
      const invalidMessage = createValidMessage({
        text: "",
      });
      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for invalid timestamp type", () => {
      const invalidMessage = createValidMessage({
        // @ts-expect-error Testing invalid timestamp type
        timestamp: "not a number",
      });
      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for invalid userId type", () => {
      const invalidMessage = createValidMessage({
        // @ts-expect-error Testing invalid userId type
        userId: 123,
      });
      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for missing userId", () => {
      const invalidMessage = createValidMessage();
      const { userId, ...invalidMessageWithoutUserId } = invalidMessage;
      expect(() => messageSchema.parse(invalidMessageWithoutUserId)).toThrow();
    });
  });
});
