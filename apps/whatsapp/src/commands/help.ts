import type { proto } from "@whiskeysockets/baileys";
import { oneLine, stripIndents } from "common-tags";
import { BOT_NAME, BOT_PREFIX, CMD_PREFIX } from "../constants";
import { invalidArgumentMessage } from "./invalid_command";

export async function handleHelp(message: proto.IWebMessageInfo, args: string) {
  let reply: string;

  switch (args) {
    case "help":
      reply = helpHelpMessage;
      break;
    case "ping":
      reply = pingHelpMessage;
      break;
    case "":
      reply = helpMessage;
      break;
    default:
      reply = invalidArgumentMessage(args);
      break;
  }

  return reply;
}

const helpMessage = stripIndents`${BOT_PREFIX}Comandos disponíveis:

🆘 *${CMD_PREFIX}help _<comando>_*
Mostra os comandos disponíveis e como usá-los.
- Digite *${CMD_PREFIX}help _<comando>_* para mais informações sobre um comando específico.

🏓 *${CMD_PREFIX}ping*
Verifica se o bot está funcionando respondendo com '*_pong!_*'.
`;

const helpHelpMessage = stripIndents`Olha só, que esperto!

Não vou te ajudar com isso não, você já sabe o que está fazendo.

Espertinho(a) 😏
`;

const pingHelpMessage = stripIndents`🏓 *${CMD_PREFIX}ping*
Verifica se o bot está funcionando respondendo com '*_pong!_*'.`;
