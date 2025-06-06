import { config } from "@eda/config";

export const CMD_PREFIX = config.services.whatsapp.cmd_prefix;
export const BOT_PREFIX = config.services.whatsapp.bot_prefix;
export const BOT_NAME = config.services.whatsapp.bot_name;
export const ENABLE_REACTIONS = config.services.whatsapp.enable_reactions;
export const ENABLE_TTS = config.services.whatsapp.enable_tts; // Add TTS enable flag
export const ALLOWED_USERS = config.access.allowed_users;
export const BLOCKED_USERS = config.access.blocked_users;
export const IGNORE_MESSAGES_WARNING =
  config.services.whatsapp.ignore_messages_warning;
