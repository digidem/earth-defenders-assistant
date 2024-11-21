import { describe, expect, it } from "vitest";
import { type MetaValue, saveProfileSchema } from "../schemas/profiles.schema";

interface ProfileParams {
  id?: string;
  userId: string;
  biome: string;
  ethnicGroup: string;
  territory: string;
  community: string;
  meta?: Record<string, MetaValue>;
}

// Test factories
function createValidProfile(overrides?: Partial<ProfileParams>): ProfileParams {
  return {
    userId: "user123",
    biome: "amazon",
    ethnicGroup: "yanomami",
    territory: "raposa-serra-do-sol",
    community: "surumu",
    ...overrides,
  };
}

describe("Save Profile Schema Validation", () => {
  describe("valid profiles", () => {
    it("should parse a complete valid profile", () => {
      const validProfile = createValidProfile();
      const result = saveProfileSchema.parse(validProfile);
      expect(result).toEqual(validProfile);
    });

    it("should accept an optional id field", () => {
      const validProfile = createValidProfile({ id: "123" });
      const result = saveProfileSchema.parse(validProfile);
      expect(result).toEqual(validProfile);
    });

    it("should accept valid meta data with different types", () => {
      const validProfile = createValidProfile({
        meta: {
          lastVisit: "2024-01-01",
          visitsCount: 5,
          isActive: true,
          lastLocation: null,
          languages: ["portuguese", "yanomami"],
          preferences: {
            notifications: true,
            language: "pt",
            timezone: "America/Manaus",
          },
        },
      });
      const result = saveProfileSchema.parse(validProfile);
      expect(result).toEqual(validProfile);
    });
  });

  describe("invalid profiles", () => {
    it("should throw an error for missing required fields", () => {
      const invalidProfile = {
        userId: "user123",
        // Missing other required fields
      };

      expect(() => saveProfileSchema.parse(invalidProfile)).toThrow();
    });

    it("should throw an error for empty strings", () => {
      const invalidProfile = createValidProfile({ biome: "" });
      expect(() => saveProfileSchema.parse(invalidProfile)).toThrow();
    });

    it("should throw an error for invalid meta data types", () => {
      const invalidProfile = createValidProfile({
        meta: {
          // @ts-expect-error Testing invalid meta value type
          complexValue: { nested: { function: () => {} } },
        },
      });
      expect(() => saveProfileSchema.parse(invalidProfile)).toThrow();
    });

    it("should throw an error for invalid data types", () => {
      const invalidProfile = createValidProfile({
        // @ts-expect-error Testing invalid string type
        biome: 123,
      });
      expect(() => saveProfileSchema.parse(invalidProfile)).toThrow();
    });
  });
});
