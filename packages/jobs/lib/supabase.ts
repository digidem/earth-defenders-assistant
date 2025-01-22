import { config } from "@eda/config";
import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  config.databases.supabase.url,
  config.api_keys.supabase.service_key,
);
