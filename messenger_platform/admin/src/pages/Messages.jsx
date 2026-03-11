import React, { useEffect, useState } from "react";
import { getContacts, getMessages, sendSingle } from "../api/client";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  sent: "bg-blue-100 text-blue-700",
  delivered: "bg-teal-100 text-teal-700",
  read: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

const statusLabel = {
  pending: "در انتظار",
  sent: "ارسال شد",
  delivered: "تحویل داده شد",
  read: "خوانده شد ✓✓",
  failed: "ناموفق",
};

export default function Messages() {
  const [contacts, setContacts] = useState([]);
  const [messages, setMessages] = useState([]);
  const [form, setForm] = useState({ contact_id: "", platform: "telegram", content: "" });
  const [sending, setSending] = useState(false);

  const loadMessages = () =>
    getMessages().then((r) => setMessages(r.data)).catch(console.error);

  useEffect(() => {
    getContacts().then((r) => setContacts(r.data)).catch(console.error);
    loadMessages();

    // WebSocket for real-time updates
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const host = process.env.REACT_APP_API_URL
      ? process.env.REACT_APP_API_URL.replace(/^https?:\/\//, "")
      : "localhost:8000";
    const ws = new WebSocket(`${proto}://${host}/messages/ws`);
    ws.onmessage = () => loadMessages();
    return () => ws.close();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await sendSingle({ ...form, contact_id: Number(form.contact_id) });
      setForm({ ...form, content: "" });
      await loadMessages();
    } catch (err) {
      alert(err?.response?.data?.detail || "خطا در ارسال");
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">ارسال پیام تکی</h2>

      <form onSubmit={handleSend} className="bg-white rounded-xl shadow p-4 mb-6 flex flex-wrap gap-3">
        <select
          className="border rounded px-3 py-2 flex-1 min-w-[150px]"
          value={form.contact_id}
          onChange={(e) => setForm({ ...form, contact_id: e.target.value })}
          required
        >
          <option value="">انتخاب مخاطب...</option>
          {contacts.map((c) => (
            <option key={c.id} value={c.id}>{c.name} — {c.phone}</option>
          ))}
        </select>
        <select
          className="border rounded px-3 py-2"
          value={form.platform}
          onChange={(e) => setForm({ ...form, platform: e.target.value })}
        >
          {["telegram", "eitaa", "bale", "rubika", "whatsapp"].map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <textarea
          className="border rounded px-3 py-2 flex-1 min-w-[200px]"
          rows={2}
          placeholder="متن پیام..."
          value={form.content}
          onChange={(e) => setForm({ ...form, content: e.target.value })}
          required
        />
        <button
          type="submit"
          disabled={sending}
          className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 self-end"
        >
          {sending ? "در حال ارسال..." : "ارسال"}
        </button>
      </form>

      <h3 className="text-lg font-semibold mb-3">تاریخچه پیام‌ها</h3>
      <div className="bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-4 py-3 text-right">مخاطب</th>
              <th className="px-4 py-3 text-right">پلتفرم</th>
              <th className="px-4 py-3 text-right">متن</th>
              <th className="px-4 py-3">جهت</th>
              <th className="px-4 py-3">وضعیت</th>
              <th className="px-4 py-3 text-right">زمان</th>
            </tr>
          </thead>
          <tbody>
            {messages.map((m) => (
              <tr key={m.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3">{m.contact_name || m.contact_id}</td>
                <td className="px-4 py-3">{m.platform}</td>
                <td className="px-4 py-3 max-w-xs truncate">{m.content}</td>
                <td className="px-4 py-3 text-center">{m.direction === "outbound" ? "↗ ارسالی" : "↙ دریافتی"}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[m.status] || ""}`}>
                    {statusLabel[m.status] || m.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {m.read_at
                    ? `خوانده: ${new Date(m.read_at).toLocaleString("fa-IR")}`
                    : m.sent_at
                    ? new Date(m.sent_at).toLocaleString("fa-IR")
                    : new Date(m.created_at).toLocaleString("fa-IR")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
