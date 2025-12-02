// frontend/app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatMessage, fetchMe, sendChatCommand } from "../../lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ name?: string; email: string } | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Check auth on mount
  useEffect(() => {
    const init = async () => {
      const u = await fetchMe();
      if (!u) {
        router.push("/");
        return;
      }
      setUser(u);
      // initial greeting from assistant
      setMessages([
        {
          role: "assistant",
          content: `Hi ${u.name || u.email}! 👋 I can read your latest emails, summarize them, help you reply, or generate a daily digest. Try typing "show my last 5 emails".`,
        },
      ]);
    };
    init();
  }, [router]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const newUserMessage: ChatMessage = { role: "user", content: input.trim() };

    const current = [...messages, newUserMessage];
    setMessages(current);
    setInput("");
    setLoading(true);

    try {
      const responseMessages = await sendChatCommand(newUserMessage.content, current);
      setMessages(responseMessages);
    } catch (err) {
      console.error(err);
      setMessages([
        ...current,
        {
          role: "assistant",
          content: "Something went wrong contacting the server. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "#020617",
        color: "white",
      }}
    >
      <header
        style={{
          padding: "0.75rem 1.5rem",
          borderBottom: "1px solid #1e293b",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "#020617",
        }}
      >
        <div>
          <h1 style={{ fontSize: "1.2rem", fontWeight: 600 }}>Email Assistant</h1>
          {user && (
            <p style={{ fontSize: "0.85rem", opacity: 0.75 }}>
              Signed in as {user.name || user.email}
            </p>
          )}
        </div>
      </header>

      <section
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          maxWidth: 900,
          width: "100%",
          margin: "0 auto",
          padding: "1rem 1.5rem 1rem",
          gap: "1rem",
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "1rem",
            borderRadius: "1rem",
            border: "1px solid #1e293b",
            background: "#020617",
          }}
        >
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "0.5rem",
              }}
            >
              <div
                style={{
                  maxWidth: "80%",
                  padding: "0.6rem 0.9rem",
                  borderRadius: "0.8rem",
                  background:
                    m.role === "user" ? "#0ea5e9" : m.role === "system" ? "#111827" : "#1e293b",
                  color: "white",
                  whiteSpace: "pre-wrap",
                  fontSize: "0.95rem",
                }}
              >
                {m.content}
              </div>
            </div>
          ))}
          {messages.length === 0 && (
            <p style={{ opacity: 0.6, fontSize: "0.9rem" }}>
              No messages yet. Ask the assistant to show your latest emails.
            </p>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Try: "Show my last 5 emails" or "Give me today&apos;s email digest"'
            style={{
              width: "100%",
              minHeight: "70px",
              borderRadius: "0.75rem",
              border: "1px solid #1e293b",
              padding: "0.75rem",
              background: "#020617",
              color: "white",
              resize: "vertical",
            }}
          />
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button
              onClick={handleSend}
              disabled={loading}
              style={{
                padding: "0.6rem 1.2rem",
                borderRadius: "999px",
                border: "none",
                background: "#22c55e",
                color: "black",
                fontWeight: 600,
                cursor: loading ? "not-allowed" : "pointer",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? "Working..." : "Send"}
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
