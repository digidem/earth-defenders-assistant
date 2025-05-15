import { stripIndents } from "common-tags";
import { BOT_PREFIX, CMD_PREFIX } from "../constants";

export const helpStatement = stripIndents`Digite *_${CMD_PREFIX}help_* para ver os comandos disponíveis.`;

export function invalidArgumentMessage(args: string, usage?: string) {
  return stripIndents`${BOT_PREFIX}Argumento inválido: _"${args}"_

  ${usage ? `Uso correto: *_${CMD_PREFIX}${usage}_*\n` : ""}
  ${helpStatement}
  `;
}

export function unauthorizedCommandFor(command: string) {
  return stripIndents`
${BOT_PREFIX}Acesso negado: Você não é admin neste grupo.

Apenas admins podem usar o comando *${command}*

${helpStatement}`;
}
