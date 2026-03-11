import React, { useEffect, useState } from "react";
import { getContacts, getContactHistory } from "../api/client";

const STATUS_ICONS = { pending: "⏳", sent: "✉️", delivered: "📬", read: "✓✓", failed: "❌" };

export default function History() {
  const [contacts, setContacts] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [history, setHistory] = useState([]);

  useEffect(() => {
    getContacts().then((r) => setContacts(r.data)).catch(console.error);
  }, []);

  const loadHistory = async (id) => {
    setSelectedId(id);
    if (!id) { setHistory([]); return; }
    try {
      const r = await getContactHistory(id);
      setHistory(r.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">تاریخچه پیام‌ها</h2>
      <div className="mb-4">
        <select
          className="border rounded px-3 py-2 w-64"
          value={selectedId}
          onChange={(e) => loadHistory(e.target.value)}
        >
          <option value="">انتخاب مخاطب...</option>
          {contacts.map((c) => (
            <option key={c.id} value={c.id}>{c.name} — {c.phone}</option>
          ))}
        </select>
      </div>

      {history.length === 0 && selectedId && (
        <p className="text-gray-400">هیچ پیامی برای این مخاطب ثبت نشده است.</p>
      )}

      <div className="space-y-2">
        {history.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.direction === "outbound" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-lg rounded-xl px-4 py-3 text-sm shadow ${
                m.direction === "outbound"
                  ? "bg-green-100 text-green-900"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <p>{m.content}</p>
              <div className="flex items-center gap-2 mt-1 text-xs opacity-60">
                <span>{m.platform}</span>
                <span>{new Date(m.created_at).toLocaleString("fa-IR")}</span>
                {m.direction === "outbound" && (
                  <span title={m.read_at ? `خوانده: ${new Date(m.read_at).toLocaleString("fa-IR")}` : ""}>
                    {STATUS_ICONS[m.status] || m.status}
                    {m.status === "read" && " خوانده شد"}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
