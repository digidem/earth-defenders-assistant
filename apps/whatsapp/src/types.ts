import type { ChatId } from "whatsapp-web.js";

export interface FormattedMessage {
	id: string;
	userId: string;
	chatId: ChatId;
	text: string;
	timestamp: number;
	processed: boolean;
	mediaPath?: string;
	meta: {
		quotedMessage?: string;
		fromMe: boolean;
		self: boolean;
		_serialized: string;
		type: string;
		location: {
			lat: number;
			lng: number;
		} | null;
		isGroup: boolean;
		groupMetadata: {
			id: {
				server: string;
				user: string;
				_serialized: string;
			};
			name: string;
			participants: {
				id: string;
				isAdmin: boolean;
				isSuperAdmin: boolean;
			}[];
		};
		from: string;
		to: string;
		author: string;
		ack: number;
		hasReaction: boolean;
		mentionedIds: string[];
		groupMentions: string[];
		links: { link: string; isSuspicious: boolean }[];
	};
}

export interface MockMessage {
	id: { id: string; _serialized: string; self: boolean };
	from: string;
	body: string;
	timestamp: number;
	fromMe: boolean;
	hasMedia: boolean;
	type: string;
	getChat: () => Promise<{
		isGroup: boolean;
		name: string;
		participants: { id: string; isAdmin: boolean; isSuperAdmin: boolean }[];
	}>;
	author: string;
	ack: number;
	hasReaction: boolean;
	mentionedIds: { _serialized: string }[];
	groupMentions: { _serialized: string }[];
	links: { link: string; isSuspicious: boolean }[];
	to: string;
	downloadMedia?: () => Promise<{ data: string | Buffer; mimetype: string }>;
}
