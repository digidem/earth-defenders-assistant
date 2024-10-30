import { mock } from "bun:test";
import type { RawMessage } from "./types";

export const mockProcessAIMessage = mock(() => {});

export const mockApi = {
	processAIMessage: mockProcessAIMessage,
};

export function generateMockRawMessage(
	overrides: Partial<RawMessage> = {},
): RawMessage {
	return {
		id: "1",
		userId: "user1",
		text: "Test message",
		timestamp: Date.now(),
		processed: false,
		...overrides,
		meta: {
			type: "chat",
			to: "recipient1",
			...(overrides.meta || {}),
		},
	};
}
