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

const helpMessage = stripIndents`${BOT_PREFIX}Available commands:

🆘 *${CMD_PREFIX}help _<command>_*
Displays the available commands, their functionalities and how to use them.
- Run *${CMD_PREFIX}help _<command>_* for more information about a specific command.

🏓 *${CMD_PREFIX}ping*
Checks if the bot is alive by responding with '*_pong!_*'.
`;

const helpHelpMessage = stripIndents`I see what you did there.

That's pretty meta, but I'm not gonna help you with that.

Smart ass.
`;

const pingHelpMessage = stripIndents`🏓 *${CMD_PREFIX}ping*
Checks if the bot is alive by responding with '*_pong!_*'.`;
