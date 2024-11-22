import { describe, expect, it } from "vitest";
import {
  type MetaValue,
  saveGrantCallSchema,
} from "../schemas/grant-calls.schema";

interface GrantCallParams {
  id?: string;
  title: string;
  description: string;
  organization: string;
  funding_amount: number;
  deadline: string;
  focus_areas: string[];
  eligibility_criteria: string[];
  requirements: string[];
  status: "open" | "closed" | "draft";
  meta?: Record<string, MetaValue>;
}

// Test factories
function createValidGrantCall(
  overrides?: Partial<GrantCallParams>,
): GrantCallParams {
  return {
    title: "Environmental Conservation Grant",
    description: "Support for local conservation initiatives",
    organization: "Green Foundation",
    funding_amount: 50000,
    deadline: "2024-12-31",
    focus_areas: ["conservation", "biodiversity"],
    eligibility_criteria: [
      "Indigenous communities",
      "Non-profit organizations",
    ],
    requirements: ["Project proposal", "Budget breakdown"],
    status: "open",
    ...overrides,
  };
}

describe("Save Grant Call Schema Validation", () => {
  describe("valid grant calls", () => {
    it("should parse a complete valid grant call", () => {
      const validGrantCall = createValidGrantCall();
      const result = saveGrantCallSchema.parse(validGrantCall);
      expect(result).toEqual(validGrantCall);
    });

    it("should accept an optional id field", () => {
      const validGrantCall = createValidGrantCall({ id: "123" });
      const result = saveGrantCallSchema.parse(validGrantCall);
      expect(result).toEqual(validGrantCall);
    });

    it("should accept valid meta data with different types", () => {
      const validGrantCall = createValidGrantCall({
        meta: {
          category: "environmental",
          priority: 1,
          active: true,
          lastUpdated: null,
          tags: ["important", "urgent"],
          details: {
            region: "north",
            maxAmount: 100000,
            restricted: false,
          },
        },
      });
      const result = saveGrantCallSchema.parse(validGrantCall);
      expect(result).toEqual(validGrantCall);
    });

    it("should accept all valid status values", () => {
      const statuses = ["open", "closed", "draft"] as const;
      for (const status of statuses) {
        const validGrantCall = createValidGrantCall({ status });
        expect(saveGrantCallSchema.parse(validGrantCall)).toEqual(
          validGrantCall,
        );
      }
    });
  });

  describe("invalid grant calls", () => {
    it("should throw an error for missing required fields", () => {
      const invalidGrantCall = {
        title: "Test Grant",
        // Missing other required fields
      };

      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });

    it("should throw an error for negative funding amount", () => {
      const invalidGrantCall = createValidGrantCall({ funding_amount: -1000 });
      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });

    it("should throw an error for invalid status", () => {
      const invalidGrantCall = createValidGrantCall({
        // @ts-expect-error Testing invalid status
        status: "pending",
      });
      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });

    it("should throw an error for invalid array fields", () => {
      const invalidGrantCall = createValidGrantCall({
        // @ts-expect-error Testing invalid array type
        focus_areas: "conservation",
      });
      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });

    it("should throw an error for invalid meta data types", () => {
      const invalidGrantCall = createValidGrantCall({
        meta: {
          // @ts-expect-error Testing invalid meta value type
          complexValue: { nested: { function: () => {} } },
        },
      });
      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });

    it("should throw an error for invalid data types", () => {
      const invalidGrantCall = createValidGrantCall({
        // @ts-expect-error Testing invalid number type
        funding_amount: "50000",
      });
      expect(() => saveGrantCallSchema.parse(invalidGrantCall)).toThrow();
    });
  });
});
