import { describe, expect, it } from "vitest";
import { querySchema } from "../schemas/received-messages.schema";

interface QueryParams {
  userId?: string;
  limit?: number;
  offset?: number;
  fromTimestamp?: number;
  toTimestamp?: number;
}

// Test factories
function createValidQuery(overrides?: Partial<QueryParams>): QueryParams {
  return {
    userId: "123",
    limit: 10,
    offset: 0,
    fromTimestamp: 1000000,
    toTimestamp: 2000000,
    ...overrides,
  };
}

describe("Received Messages Query Schema Validation", () => {
  describe("valid queries", () => {
    it("should parse a complete valid query", () => {
      const validQuery = createValidQuery();
      const result = querySchema.parse(validQuery);
      expect(result).toEqual(validQuery);
    });

    it("should allow optional fields to be omitted", () => {
      const validQuery = { userId: "456" };
      const result = querySchema.parse(validQuery);
      expect(result).toEqual(validQuery);
    });

    it("should accept zero values for numeric fields", () => {
      const validQuery = createValidQuery({ limit: 0, offset: 0 });
      const result = querySchema.parse(validQuery);
      expect(result).toEqual(validQuery);
    });

    it("should accept equal fromTimestamp and toTimestamp", () => {
      const timestamp = 1500000;
      const validQuery = createValidQuery({
        fromTimestamp: timestamp,
        toTimestamp: timestamp,
      });
      const result = querySchema.parse(validQuery);
      expect(result).toEqual(validQuery);
    });
  });

  describe("invalid queries", () => {
    it("should throw an error for invalid data types", () => {
      const invalidQuery = { limit: "10" };

      expect(() => querySchema.parse(invalidQuery)).toThrow(
        "Expected number, received string",
      );
    });

    it("should throw an error for negative limit", () => {
      const invalidQuery = createValidQuery({ limit: -1 });
      expect(() => querySchema.parse(invalidQuery)).toThrow();
    });

    it("should throw an error for negative offset", () => {
      const invalidQuery = createValidQuery({ offset: -1 });
      expect(() => querySchema.parse(invalidQuery)).toThrow();
    });

    it("should throw an error for negative timestamps", () => {
      expect(() => querySchema.parse({ fromTimestamp: -1 })).toThrow();
      expect(() => querySchema.parse({ toTimestamp: -1 })).toThrow();
    });
  });
});
