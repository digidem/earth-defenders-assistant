import { afterEach, beforeEach, describe, expect, it, mock } from "bun:test";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { getMessages } from "../database";
import { handleMessage } from "../messageHandler";
import type { FormattedMessage, MockMessage } from "../types";
import { cleanupTestDB } from "./utils";

describe("Message Handler", () => {
	let TEST_APP_FOLDER: string;
	let mockMediaDir: string;

	beforeEach(() => {
		TEST_APP_FOLDER = path.join(
			os.tmpdir(),
			`test-earth-defenders-assistant-${crypto.randomBytes(8).toString("hex")}`,
		);
		mockMediaDir = path.join(TEST_APP_FOLDER, "media");

		fs.mkdirSync(TEST_APP_FOLDER, { recursive: true });
		fs.mkdirSync(mockMediaDir);
	});

	afterEach(() => {
		cleanupTestDB(TEST_APP_FOLDER);
	});

	const createMockMessage = (overrides = {}): MockMessage => ({
		id: { id: "test-id", _serialized: "test-id", self: false },
		from: "test-user",
		body: "Test message",
		timestamp: Date.now(),
		fromMe: false,
		hasMedia: false,
		type: "chat",
		getChat: mock(() =>
			Promise.resolve({
				isGroup: true,
				name: "Casa de Palha",
				participants: [],
			}),
		),
		author: "",
		ack: 0,
		hasReaction: false,
		mentionedIds: [],
		groupMentions: [],
		links: [],
		to: "test-group",
		...overrides,
	});

	const messageGenerator = (): MockMessage[] => [
		createMockMessage(), // Text message
		createMockMessage({
			id: {
				id: "media-message-id",
				self: false,
				_serialized: "media-message-id",
			},
			body: "This is a media message",
			type: "image",
			hasMedia: true,
			downloadMedia: mock(() =>
				Promise.resolve({
					data: Buffer.from("fake-image-data").toString("base64"),
					mimetype: "image/jpeg",
				}),
			),
		}), // Media message
	];

	it.each(messageGenerator())(
		"should handle different types of messages correctly",
		async (mockMessage: MockMessage) => {
			await handleMessage(mockMessage, TEST_APP_FOLDER);

			const savedMessages = getMessages(TEST_APP_FOLDER);
			expect(savedMessages).toHaveLength(1);

			const savedMessage = savedMessages[0] as FormattedMessage;
			expect(savedMessage).toMatchObject({
				id: mockMessage.id.id,
				userId: mockMessage.from,
				text: mockMessage.body,
				timestamp: expect.any(Number),
				chatId: expect.any(Object),
				processed: false,
				meta: expect.objectContaining({
					fromMe: mockMessage.fromMe,
					self: mockMessage.id.self,
					_serialized: mockMessage.id._serialized,
					type: mockMessage.type,
					isGroup: true,
					from: mockMessage.from,
					to: mockMessage.to,
					author: mockMessage.author,
					ack: mockMessage.ack,
					hasReaction: mockMessage.hasReaction,
					mentionedIds: expect.any(Array),
					groupMentions: expect.any(Array),
					links: expect.any(Array),
				}),
			});
			if (mockMessage.hasMedia) {
				expect(savedMessage.mediaPath).toBeTruthy();
				if (savedMessage.mediaPath) {
					expect(savedMessage.mediaPath).toMatch(
						new RegExp(`${mockMessage.id.id}\\.jpeg$`),
					);
					expect(fs.existsSync(savedMessage.mediaPath)).toBe(true);
				} else {
					throw new Error("Expected mediaPath to be defined");
				}
			} else {
				expect(savedMessage.mediaPath).toBeUndefined();
			}
		},
	);
});
