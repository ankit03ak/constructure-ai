// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchAuthUrl, fetchMe } from "../lib/api";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const user = await fetchMe();
        if (user) {
          router.push("/dashboard");
        }
      } catch (err) {
        console.error(err);
      } finally {
        setCheckingAuth(false);
        setLoading(false);
      }
    };
    check();
  }, [router]);

  const handleLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const authUrl = await fetchAuthUrl();
      window.location.href = authUrl;
    } catch (err) {
      console.error(err);
      setError("Failed to start Google login. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1.5rem",
        background: "#0f172a",
        color: "white",
      }}
    >
      <div
        style={{
          maxWidth: 420,
          width: "100%",
          background: "#020617",
          padding: "2rem",
          borderRadius: "1rem",
          boxShadow: "0 20px 40px rgba(0,0,0,0.4)",
          border: "1px solid #1e293b",
        }}
      >
        <h1 style={{ fontSize: "1.6rem", fontWeight: 700, marginBottom: "0.5rem" }}>
          Constructure AI – Email Assistant
        </h1>
        <p style={{ opacity: 0.8, marginBottom: "1.5rem" }}>
          Sign in with Google to let the assistant read, summarize, reply to, and manage your
          Gmail.
        </p>

        {error && (
          <p style={{ color: "#f97373", marginBottom: "1rem", fontSize: "0.9rem" }}>{error}</p>
        )}

        <button
          onClick={handleLogin}
          disabled={loading || checkingAuth}
          style={{
            width: "100%",
            padding: "0.75rem 1rem",
            borderRadius: "999px",
            border: "none",
            fontWeight: 600,
            fontSize: "0.95rem",
            cursor: loading ? "not-allowed" : "pointer",
            background: "#f97316",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading || checkingAuth ? "Checking / Redirecting..." : "Sign in with Google"}
        </button>

        <p style={{ fontSize: "0.8rem", marginTop: "1rem", opacity: 0.7 }}>
          You&apos;ll be redirected to Google for secure authentication.
        </p>
      </div>
    </main>
  );
}
