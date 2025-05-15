import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { logger } from "@eda/logger";
import type { Message } from "whatsapp-web.js";
import { saveMessage } from "./database";
import type { FormattedMessage } from "./types";

const DEFAULT_APP_FOLDER = path.join(
  os.homedir(),
  ".earth-defenders-assistant",
);

export const handleMessage = async (
  message: Message,
  appFolder: string = DEFAULT_APP_FOLDER,
) => {
  const mediaDir = path.join(appFolder, "media");
  try {
    if (!fs.existsSync(mediaDir)) {
      fs.mkdirSync(mediaDir);
    }

    let mediaPath: string | undefined;

    const chat = await message.getChat();
    const groups = ["Casa de Palha"]; // Add your group IDs or names here

    const isGroup = chat.isGroup;
    const groupId = message.fromMe ? message.to : message.from;
    const groupName = chat.name;

    const isDebugMode = process.env.DEBUG === "true";
    const isFromSelf = message.fromMe;
    const isRelevantGroup =
      isGroup && (groups.includes(groupId) || groups.includes(groupName));
    if ((isDebugMode && isFromSelf) || isRelevantGroup) {
      const formattedMessage: FormattedMessage = {
        id: message.id.id,
        userId: message.from,
        text: message.body,
        timestamp: message.timestamp,
        chatId: {
          server: "g.us",
          user: message.from,
          _serialized: `${message.from}@g.us`,
        },
        processed: false,
        mediaPath,
        meta: {
          fromMe: message.fromMe,
          self: message.id.self,
          _serialized: message.id._serialized,
          type: message.type,
          location:
            message.type === "location"
              ? {
                  lat: message.location?.latitude
                    ? Number(message.location.latitude)
                    : 0,
                  lng: message.location?.longitude
                    ? Number(message.location.longitude)
                    : 0,
                }
              : null,
          isGroup,
          groupMetadata: {
            id: {
              server: "g.us",
              user: groupId,
              _serialized: `${groupId}@g.us`,
            },
            name: groupName,
            participants: chat.participants?.map((participant) => ({
              id: participant.id,
              isAdmin: participant.isAdmin,
              isSuperAdmin: participant.isSuperAdmin,
            })),
          },
          from: message.from,
          to: message.to,
          author: message.author || "",
          ack: message.ack,
          hasReaction: message.hasReaction || false,
          mentionedIds: message.mentionedIds?.map((id) => id._serialized) || [],
          groupMentions:
            message.groupMentions?.map((id) => id._serialized) || [],
          links: message.links || [],
        },
      };
      if (message.hasQuotedMsg) {
        const quotedMessage = await message.getQuotedMessage();
        console.log(quotedMessage);
        formattedMessage.quotedMessage = quotedMessage;
      }
      if (message.hasMedia) {
        const media = await message.downloadMedia();
        mediaPath = path.join(
          mediaDir,
          `${message.id.id}.${media.mimetype.split("/")[1]}`,
        );
        fs.writeFileSync(mediaPath, media.data, "base64");
        logger.info(`Media saved to ${mediaPath}`);
        formattedMessage.mediaPath = mediaPath;
      }
      saveMessage(formattedMessage, appFolder);
      logger.info(`Message saved: ${message.id.id}`);
    }
  } catch (error) {
    logger.error(`Error processing message: ${error}`);
  }
};
