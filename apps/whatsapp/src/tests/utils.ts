import fs from "node:fs";
import path from "node:path";
import type { FormattedMessage } from "../types";

export const TEST_DB_PATH = path.join("/tmp", "test_message_db.json");

export function cleanupTestDB() {
	if (fs.existsSync(TEST_DB_PATH)) {
		fs.unlinkSync(TEST_DB_PATH);
	}
}

export function createMockMessage(
	overrides: Partial<FormattedMessage> = {},
): FormattedMessage {
	return {
		id: "test-id",
		userId: "test-user",
		chatId: "test-chat",
		text: "Test message",
		timestamp: Date.now(),
		processed: false,
		meta: {
			fromMe: false,
		},
		...overrides,
	};
}
