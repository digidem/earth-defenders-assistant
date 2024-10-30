"use client";

import { createClient } from "@eda/supabase/client";
import { Button } from "@eda/ui/button";
import { Icons } from "@eda/ui/icons";

export function SignOut() {
  const supabase = createClient();

  const handleSignOut = () => {
    supabase.auth.signOut();
  };

  return (
    <Button
      onClick={handleSignOut}
      variant="outline"
      className="font-mono gap-2 flex items-center"
    >
      <Icons.SignOut className="size-4" />
      <span>Sign out</span>
    </Button>
  );
}
