import { config } from "@eda/config";
import { createBrowserClient } from "@supabase/ssr";
import type { Database } from "../types";

export const createClient = () =>
  createBrowserClient<Database>(
    config.databases.supabase.url,
    config.api_keys.supabase.anon_key,
  );
