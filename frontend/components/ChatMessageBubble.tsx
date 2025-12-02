// frontend/components/ChatMessageBubble.tsx
import React from "react";
import { ChatMessage } from "../lib/api";

export default function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "0.5rem",
      }}
    >
      <div
        style={{
          maxWidth: "75%",
          padding: "0.7rem 1rem",
          borderRadius: "0.8rem",
          background: isUser ? "#0ea5e9" : "#1e293b",
          whiteSpace: "pre-wrap",
          fontSize: "0.95rem",
        }}
      >
        {message.content}
      </div>
    </div>
  );
}
