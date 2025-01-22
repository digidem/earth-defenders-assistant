"use server";

import { helloWorldTask } from "@eda/jobs/trigger/example";
import { tasks } from "@trigger.dev/sdk/v3";

export async function myTask() {
  try {
    // Remove task option and pass payload directly
    const handle = await tasks.trigger("hello-world", "James");

    return { handle };
  } catch (error) {
    console.error(error);
    return {
      error: "something went wrong",
    };
  }
}
