import type { RawMessage } from '@eda/types'

interface Message {
    role: "system" | "user" | "assistant";
    content: RawMessage
}
export type Messages = Message[];
