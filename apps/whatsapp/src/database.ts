import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { tasks } from "@trigger.dev/sdk/v3";
import type { FormattedMessage } from "./types";

const DEFAULT_APP_FOLDER = path.join(
  os.homedir(),
  ".earth-defenders-assistant",
);
const getDbPath = (appFolder: string) =>
  path.join(appFolder, "message_db.json");

const ensureDirectoryExists = (directory: string) => {
  if (!fs.existsSync(directory)) {
    fs.mkdirSync(directory, { recursive: true });
  }
};

export const getMessages = (
  appFolder: string = DEFAULT_APP_FOLDER,
): FormattedMessage[] => {
  const dbPath = getDbPath(appFolder);
  if (fs.existsSync(dbPath)) {
    const data = fs.readFileSync(dbPath, "utf8");
    return JSON.parse(data);
  }
  return [];
};

export const saveMessage = async (
  message: FormattedMessage,
  appFolder: string = DEFAULT_APP_FOLDER,
) => {
  const handle = await tasks.trigger("save-received-message", message);

  //return a success response with the handle
  return Response.json(handle);
};

export const updateMessageProcessedState = (
  messageId: string,
  processed: boolean,
  appFolder: string = DEFAULT_APP_FOLDER,
) => {
  ensureDirectoryExists(appFolder);
  const dbPath = getDbPath(appFolder);
  const messages = getMessages(appFolder);
  const updatedMessages = messages.map((msg) =>
    msg.id === messageId ? { ...msg, processed } : msg,
  );
  fs.writeFileSync(dbPath, JSON.stringify(updatedMessages, null, 2), "utf8");
};
