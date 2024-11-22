import { describe, expect, it } from "vitest";
import { querySchema } from "../schemas/grant-calls.schema";

interface QueryParams {
  userId?: string;
  limit?: number;
  offset?: number;
  status?: "open" | "closed" | "draft";
  focusArea?: string;
  minAmount?: number;
  maxAmount?: number;
}

// Test factories
function createValidQuery(overrides?: Partial<QueryParams>): QueryParams {
  return {
    userId: "123",
    limit: 10,
    offset: 0,
    status: "open",
    focusArea: "tech",
    minAmount: 100,
    maxAmount: 1000,
    ...overrides,
  };
}

describe("Query Schema Validation", () => {
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
      const validQuery = createValidQuery({ minAmount: 0, maxAmount: 0 });
      const result = querySchema.parse(validQuery);
      expect(result).toEqual(validQuery);
    });
  });

  describe("invalid queries", () => {
    it("should throw an error for invalid enum value", () => {
      const invalidQuery = { status: "invalidStatus" };

      expect(() => querySchema.parse(invalidQuery)).toThrow(
        /Invalid enum value/,
      );
    });

    it("should throw an error for invalid data types", () => {
      const invalidQuery = { limit: "10" };

      expect(() => querySchema.parse(invalidQuery)).toThrow(
        "Expected number, received string",
      );
    });

    it("should throw an error for negative amounts", () => {
      expect(() => querySchema.parse({ minAmount: -100 })).toThrow();
      expect(() => querySchema.parse({ maxAmount: -50 })).toThrow();
    });

    it("should throw when maxAmount is less than minAmount", () => {
      const invalidQuery = createValidQuery({
        minAmount: 1000,
        maxAmount: 100,
      });

      expect(() => querySchema.parse(invalidQuery)).toThrow(
        "maxAmount must be greater than or equal to minAmount",
      );
    });
  });
});
