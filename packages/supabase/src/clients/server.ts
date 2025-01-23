import { config } from "@eda/config";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import type { Database } from "../types";

export const createClient = () => {
  const cookieStore = cookies();

  return createServerClient<Database>(
    config.databases.supabase.url,
    config.api_keys.supabase.service_key,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            for (const { name, value, options } of cookiesToSet) {
              cookieStore.set(name, value, options);
            }
          } catch (error) {}
        },
      },
    },
  );
};
