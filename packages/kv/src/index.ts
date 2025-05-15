import { Redis } from "@upstash/redis";
import "server-only";
//@ts-ignore
import { config } from "@eda/config";

export const client = new Redis({
  url: config.services.upstash.redis_url,
  token: config.services.upstash.redis_token,
});
