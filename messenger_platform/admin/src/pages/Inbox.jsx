import React, { useEffect, useState } from "react";
import { getInbox, adminReply } from "../api/client";

export default function Inbox() {
  const [messages, setMessages] = useState([]);
  const [replyForms, setReplyForms] = useState({});
  const [sending, setSending] = useState({});

  const load = () =>
    getInbox().then((r) => setMessages(r.data)).catch(console.error);

  useEffect(() => {
    load();
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const host = process.env.REACT_APP_API_URL
      ? process.env.REACT_APP_API_URL.replace(/^https?:\/\//, "")
      : "localhost:8000";
    const ws = new WebSocket(`${proto}://${host}/messages/ws`);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.event === "inbound_message") load();
    };
    return () => ws.close();
  }, []);

  const handleReply = async (msg) => {
    const content = replyForms[msg.id];
    if (!content?.trim()) return;
    setSending((s) => ({ ...s, [msg.id]: true }));
    try {
      await adminReply({ message_id: msg.id, content });
      setReplyForms((f) => ({ ...f, [msg.id]: "" }));
    } catch (err) {
      alert(err?.response?.data?.detail || "خطا در ارسال پاسخ");
    } finally {
      setSending((s) => ({ ...s, [msg.id]: false }));
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">صندوق دریافت (پیام‌های کاربران)</h2>
      {messages.length === 0 && (
        <p className="text-gray-400">هیچ پیام دریافتی‌ای وجود ندارد.</p>
      )}
      <div className="space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{msg.contact_name}</span>
              <span className="text-xs text-gray-400">{new Date(msg.created_at).toLocaleString("fa-IR")}</span>
            </div>
            <p className="text-xs text-gray-400 mb-2">
              {msg.contact_phone} — {msg.platform}
            </p>
            <div className="bg-blue-50 rounded-lg p-3 mb-3 text-sm">{msg.content}</div>
            <div className="flex gap-2">
              <textarea
                rows={2}
                className="border rounded px-3 py-2 flex-1 text-sm"
                placeholder="پاسخ شما..."
                value={replyForms[msg.id] || ""}
                onChange={(e) =>
                  setReplyForms((f) => ({ ...f, [msg.id]: e.target.value }))
                }
              />
              <button
                onClick={() => handleReply(msg)}
                disabled={sending[msg.id]}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm self-end"
              >
                {sending[msg.id] ? "..." : "ارسال پاسخ"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
