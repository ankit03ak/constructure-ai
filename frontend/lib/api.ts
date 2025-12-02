// frontend/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export async function fetchAuthUrl(): Promise<string> {
  const res = await fetch(`${API_URL}/auth/google/login`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to get auth URL");
  }
  const data = await res.json();
  return data.auth_url;
}

export async function fetchMe() {
  const res = await fetch(`${API_URL}/auth/me`, {
    credentials: "include",
  });
  if (!res.ok) {
    return null; // not logged in
  }
  const data = await res.json();
  return data.user;
}

export async function sendChatCommand(
  message: string,
  context: ChatMessage[] = []
): Promise<ChatMessage[]> {
  const res = await fetch(`${API_URL}/chat/command`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, context }),
  });

  if (!res.ok) {
    throw new Error("Chat command failed");
  }

  const data = await res.json();
  return data.messages as ChatMessage[];
}
