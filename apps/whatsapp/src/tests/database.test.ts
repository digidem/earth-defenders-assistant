import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import { mock } from "bun:test";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import {
	getMessages,
	saveMessage,
	updateMessageProcessedState,
} from "../database";
import { cleanupTestDB, createMockMessage } from "./utils";

const DEFAULT_APP_FOLDER = path.join(
	os.homedir(),
	".earth-defenders-assistant",
);

describe("Database functions", () => {
	let TEST_APP_FOLDER: string;

	beforeEach(() => {
		TEST_APP_FOLDER = path.join(
			os.tmpdir(),
			`test-earth-defenders-assistant-${crypto.randomBytes(8).toString("hex")}`,
		);
		cleanupTestDB(TEST_APP_FOLDER);
	});

	afterEach(() => {
		cleanupTestDB(TEST_APP_FOLDER);
	});

	it("should save and retrieve messages with custom appFolder", () => {
		const mockMessage = createMockMessage();

		saveMessage(mockMessage, TEST_APP_FOLDER);
		const messages = getMessages(TEST_APP_FOLDER);

		expect(messages).toHaveLength(1);
		expect(messages[0]).toEqual(mockMessage);
	});

	it("should update message processed state with custom appFolder", () => {
		const mockMessage = createMockMessage();
		saveMessage(mockMessage, TEST_APP_FOLDER);

		updateMessageProcessedState(mockMessage.id, true, TEST_APP_FOLDER);
		const messages = getMessages(TEST_APP_FOLDER);

		expect(messages[0].processed).toBe(true);
	});

	it("should return an empty array when no messages exist with custom appFolder", () => {
		const messages = getMessages(TEST_APP_FOLDER);

		expect(messages).toEqual([]);
	});
});
