import { describe, expect, it } from "vitest";
import { querySchema } from "../schemas/profiles.schema";

interface QueryParams {
  userId?: string;
  biome?: string;
  ethnicGroup?: string;
  territory?: string;
  community?: string;
  limit?: number;
  offset?: number;
}

// Test factories
function createValidQuery(overrides?: Partial<QueryParams>): QueryParams {
  return {
    userId: "123",
    biome: "amazon",
    ethnicGroup: "yanomami",
    territory: "raposa-serra-do-sol",
    community: "surumu",
    limit: 10,
    offset: 0,
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
      const validQuery = createValidQuery({ limit: 0, offset: 0 });
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
  });
});
