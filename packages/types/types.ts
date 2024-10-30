export interface RawMessage {
	id: string;
	userId: string;
	text: string;
	timestamp: number;
	processed: boolean;
	meta: {
		quotedMessage?: string;
		fromMe: boolean;
		_serialized: string;
		type: string;
		location: GeoLocation | null;
		isGroup: boolean;
		groupMetadata: {
			id: {
				server: string;
				user: string;
				_serialized: string;
			};
			name: string;
			participants: Array<{
				id: {
					server: string;
					user: string;
					_serialized: string;
				};
				isAdmin: boolean;
				isSuperAdmin: boolean;
			}>;
		};
		from: string;
		to: string;
		author: string;
		ack: number;
		hasReaction: boolean;
		mentionedIds: string[];
		groupMentions: string[];
		links: string[];
	};
}
export type MessageStatus =
	| "response"
	| "processed"
	| "ignore"
	| "pending"
	| "error";

export interface Message {
	id: string;
	userId: string;
	text: string;
	timestamp: number;
	processed: boolean;
	mediaPath?: string;
	location?: GeoLocation;
	status?: MessageStatus;
}

export interface ProcessedMessage extends Message {
	status: MessageStatus;
	alsoProcessed: string[];
	result?: null | string | Media | GeoLocation | undefined;
	requiredInfo?: string[];
	error?: string;
}

export interface GeoLocation {
	latitude: number;
	longitude: number;
}

export interface Media {
	type: "image" | "video" | "audio";
	url: string;
}

export interface DbSchema {
	messages: Message[];
}
