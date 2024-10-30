import { tasks } from "@trigger.dev/sdk/v3";
import dotenv from "dotenv";
import { generateWhatsAppMessage } from "./src/utils";

dotenv.config();


const systemPrompt =
  "You are an AI assistant tasked with generating a simulated WhatsApp message in JSON format. Generate a message that follows the structure of the provided template, ensuring all personal data is anonymized. The message should involve an indigenous earth defender seeking funding for their community, climate justice, and territory defense projects, including a plausible text content, timestamp, and other metadata fields.";
const userPrompt = `Generate a WhatsApp message object following this template, but with anonymized data:
      {
        "userId": "ANONYMIZED_USER_ID@c.us",
        "text": "Hi! I'm looking for funding opportunities for my community projects. Do you know of any grants or investors that might be interested?",
        "processed": false,
        "meta": {
          "fromMe": false,
          "self": "out",
          "_serialized": "true_ANONYMIZED_USER_ID@c.us_ANONYMIZED_ID_out",
          "type": "chat",
          "location": null,
          "isGroup": false,
          "groupMetadata": {
            "id": {
              "server": "g.us",
              "user": "ANONYMIZED_USER_ID@c.us",
              "_serialized": "ANONYMIZED_USER_ID@c.us@g.us"
            },
            "name": "ANONYMIZED_GROUP_NAME"
          },
          "from": "ANONYMIZED_USER_ID@c.us",
          "to": "ANONYMIZED_USER_ID@c.us",
          "author": "ANONYMIZED_USER_ID@c.us",
          "ack": 3,
          "hasReaction": false,
          "mentionedIds": [],
          "groupMentions": [],
          "links": []
        }
      }`;

const messages = [
  {
    role: "system" as const,
    content: systemPrompt,
  },
  {
    role: "user" as const,
    content: userPrompt,
  },
];


async function main() {
  try {
    console.log('Running simulator')
    const message = await generateWhatsAppMessage(messages);
    console.log('Sending message:');
    console.log(message.data.text);
    await tasks.trigger("save-received-message", message);
  } catch (error) {
    console.error("Error in message generation and saving:", error);
    // TODO: Implement proper error logging and user-friendly message
  }
}

main();
