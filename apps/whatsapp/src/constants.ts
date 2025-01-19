import dotenv from "dotenv";
import dotenvExpand from "dotenv-expand";
dotenvExpand.expand(dotenv.config());
import { config } from "@eda/config";

export const CMD_PREFIX = config.whatsapp.cmd_prefix;
export const BOT_PREFIX = config.whatsapp.bot_prefix;
export const BOT_NAME = config.whatsapp.bot_name;
export const ENABLE_REACTIONS = config.whatsapp.enable_reactions;
export const ALLOWED_USERS = process.env.ALLOWED_USERS
  ? process.env.ALLOWED_USERS.split(",")
  : [];
export const BLOCKED_USERS = process.env.BLOCKED_USERS
  ? process.env.BLOCKED_USERS.split(",")
  : [];
export const IGNORE_MESSAGES_WARNING = process.env
  .IGNORE_MESSAGES_WARNING as string;
