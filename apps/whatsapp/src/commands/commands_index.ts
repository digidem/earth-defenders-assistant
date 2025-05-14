import type { WASocket, proto } from "@whiskeysockets/baileys";
import { stripIndents } from "common-tags";
import { sock } from "../client";
import { BOT_PREFIX, CMD_PREFIX } from "../constants";
import { react, unauthorizedCommandFor } from "../utils";
import { handleHelp } from "./help";

const adminCommands = ["jailbreak", "reset", "change"];
export const helpStatement = stripIndents`Run *_${CMD_PREFIX}help_* to see the available commands.`;

export async function handleCommand(message: proto.IWebMessageInfo) {
  const messageBody = message.message?.conversation;

  if (!messageBody) {
    await react(message, "error");
    return;
  }
  const [command, ..._args] = messageBody.split(CMD_PREFIX)[1].split(" ");

  const args = _args.join(" ").toLowerCase();
  let reply: string;

  await react(message, "working");

  const chatId = message.key.remoteJid;
  if (!chatId) {
    await react(message, "error");
    return;
  }
  let isAdmin = true; // default to true for private chats
  if (chatId.endsWith("@g.us")) {
    const groupMetadata = await sock.groupMetadata(chatId);
    const senderId = message.key.participant || message.key.remoteJid;
    isAdmin = groupMetadata.participants.some(
      (participant) => participant.id === senderId && participant.admin,
    );
  }

  if (adminCommands.includes(command) && !isAdmin) {
    reply = unauthorizedCommandFor(command);
    await sock.sendMessage(chatId, { text: reply }, { quoted: message });
    await react(message, "done");
    return;
  }

  switch (command) {
    case "ping":
      reply = `${BOT_PREFIX}*_pong!_*`;
      break;

    case "help":
      reply = await handleHelp(message, args);
      break;
    default:
      reply = stripIndents`
        ${BOT_PREFIX}Comando desconhecido: _"${CMD_PREFIX + command}"_

        ${helpStatement}`;
      break;
  }

  await sock.sendMessage(chatId, { text: reply }, { quoted: message });
  await react(message, "done");
}
