import dotenv from "dotenv";
import dotenvExpand from "dotenv-expand";
dotenvExpand.expand(dotenv.config());

export const CMD_PREFIX = process.env.CMD_PREFIX?.trim() as string;
export const BOT_PREFIX = `${process.env.BOT_PREFIX?.trim()} ` as string;
export const BOT_NAME = process.env.BOT_NAME?.trim() as string;
export const ENABLE_REACTIONS = process.env.ENABLE_REACTIONS as string;
export const ALLOWED_USERS = process.env.ALLOWED_USERS
  ? process.env.ALLOWED_USERS.split(",")
  : [];
export const BLOCKED_USERS = process.env.BLOCKED_USERS
  ? process.env.BLOCKED_USERS.split(",")
  : [];
export const IGNORE_MESSAGES_WARNING = process.env
  .IGNORE_MESSAGES_WARNING as string;
