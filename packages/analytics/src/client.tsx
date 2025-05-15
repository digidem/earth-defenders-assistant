import { config } from "@eda/config";
import { logger } from "@eda/logger";
import {
  OpenPanelComponent,
  type PostEventPayload,
  useOpenPanel,
} from "@openpanel/nextjs";

const isProd = process?.env.NODE_ENV === "production";

const Provider = () => (
  <OpenPanelComponent
    clientId={config.api_keys.openpanel.client_id}
    trackAttributes={true}
    trackScreenViews={isProd}
    trackOutgoingLinks={isProd}
  />
);

const track = (options: { event: string } & PostEventPayload["properties"]) => {
  const { track: openTrack } = useOpenPanel();

  if (!isProd) {
    logger.info("Track", options);
    return;
  }

  const { event, ...rest } = options;
  openTrack(event, rest);
};

export { Provider, track };
