import { config } from "@eda/config";
import { logger } from "@eda/logger";
import { OpenPanel, type PostEventPayload } from "@openpanel/nextjs";
import { waitUntil } from "@vercel/functions";

type Props = {
  userId?: string;
  fullName?: string | null;
};

export const setupAnalytics = async (options?: Props) => {
  const { userId, fullName } = options ?? {};

  const client = new OpenPanel({
    clientId: config.api_keys.openpanel.client_id,
    clientSecret: config.api_keys.openpanel.secret,
  });

  if (userId && fullName) {
    const [firstName, lastName] = fullName.split(" ");

    waitUntil(
      client.identify({
        profileId: userId,
        firstName,
        lastName,
      }),
    );
  }

  return {
    track: (options: { event: string } & PostEventPayload["properties"]) => {
      if (process.env.NODE_ENV !== "production") {
        logger.info("Track", options);
        return;
      }

      const { event, ...rest } = options;
      waitUntil(client.track(event, rest));
    },
  };
};
