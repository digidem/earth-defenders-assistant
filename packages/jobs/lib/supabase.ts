// TODO: should be moved to @eda/supabase, but currently having error: SyntaxError: Cannot use import statement outside a module
import { createClient } from "@supabase/supabase-js";
// Generate the Typescript types using the Supabase CLI: https://supabase.com/docs/guides/api/rest/generating-types
// import type { Database } from "database.types";

// Create a single Supabase client for interacting with your database
// 'Database' supplies the type definitions to supabase-js
// export const supabase = createClient<Database>(
export const supabase = createClient(
  // These details can be found in your Supabase project settings under `API`
  process.env.SUPABASE_PROJECT_URL as string, // e.g. https://abc123.supabase.co - replace 'abc123' with your project ID
  process.env.SUPABASE_SERVICE_ROLE_KEY as string, // Your service role secret key
);
