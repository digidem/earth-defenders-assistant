import { describe, expect, it } from "vitest";
import { messageSchema } from "../schemas/received-messages.schema";

interface MessageParams {
  id: string;
  _id: string;
  from: string;
  to: string;
  userId: string;
  data: {
    text: string;
  };
  timestamp: number;
  type: string;
  isGroupChat: boolean;
  chatId: string;
  created: string;
}

// Test factories
function createValidMessage(overrides?: Partial<MessageParams>): MessageParams {
  return {
    id: "msg123",
    _id: "msg123_internal",
    from: "sender123",
    to: "recipient123",
    userId: "user123",
    data: {
      text: "Hello, this is a test message",
    },
    timestamp: Date.now(),
    type: "chat",
    isGroupChat: false,
    chatId: "chat123",
    created: new Date().toISOString(),
    ...overrides,
  };
}

describe("Save Received Message Schema Validation", () => {
  describe("valid messages", () => {
    it("should parse a complete valid message", () => {
      const validMessage = createValidMessage();
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });

    it("should accept group chat messages", () => {
      const validMessage = createValidMessage({
        isGroupChat: true,
        to: "group123",
      });
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });

    it("should accept messages with different types", () => {
      const validMessage = createValidMessage({
        type: "media",
      });
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });

    it("should accept valid timestamps", () => {
      const validMessage = createValidMessage({
        timestamp: 1234567890,
        created: "2024-01-01T00:00:00.000Z",
      });
      const result = messageSchema.parse(validMessage);
      expect(result).toEqual(validMessage);
    });
  });

  describe("invalid messages", () => {
    it("should throw an error for missing required fields", () => {
      const invalidMessage = {
        id: "msg123",
        // Missing other required fields
      };

      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for invalid data structure", () => {
      const invalidMessage = createValidMessage({
        // @ts-expect-error Testing invalid data structure
        data: "not an object",
      });
      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });

    it("should throw an error for missing text in data", () => {
      const invalidMessage = createValidMessage({
        // @ts-expect-error Testing missing text
        data: {},
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

    it("should throw an error for invalid boolean type", () => {
      const invalidMessage = createValidMessage({
        // @ts-expect-error Testing invalid boolean type
        isGroupChat: "true",
      });
      expect(() => messageSchema.parse(invalidMessage)).toThrow();
    });
  });
});
