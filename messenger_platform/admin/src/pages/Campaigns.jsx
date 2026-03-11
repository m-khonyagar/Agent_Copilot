import React, { useEffect, useState } from "react";
import { getContacts, getCampaigns, createCampaign } from "../api/client";

const STATUS_COLORS = {
  draft: "bg-gray-100 text-gray-700",
  scheduled: "bg-yellow-100 text-yellow-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function Campaigns() {
  const [contacts, setContacts] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [form, setForm] = useState({
    name: "",
    platform: "telegram",
    content: "",
    scheduled_at: "",
    rate_limit_per_day: "",
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    getContacts().then((r) => setContacts(r.data)).catch(console.error);
    getCampaigns().then((r) => setCampaigns(r.data)).catch(console.error);
  }, []);

  const toggleContact = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!selectedIds.length) { alert("حداقل یک مخاطب انتخاب کنید"); return; }
    setCreating(true);
    try {
      await createCampaign({
        ...form,
        contact_ids: selectedIds,
        rate_limit_per_day: form.rate_limit_per_day ? Number(form.rate_limit_per_day) : null,
        scheduled_at: form.scheduled_at || null,
      });
      setForm({ name: "", platform: "telegram", content: "", scheduled_at: "", rate_limit_per_day: "" });
      setSelectedIds([]);
      const r = await getCampaigns();
      setCampaigns(r.data);
    } catch (err) {
      alert(err?.response?.data?.detail || "خطا");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">کمپین‌های پیام دسته‌جمعی</h2>

      <form onSubmit={handleCreate} className="bg-white rounded-xl shadow p-4 mb-6 space-y-3">
        <div className="flex flex-wrap gap-3">
          <input
            className="border rounded px-3 py-2 flex-1 min-w-[150px]"
            placeholder="نام کمپین"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <select
            className="border rounded px-3 py-2"
            value={form.platform}
            onChange={(e) => setForm({ ...form, platform: e.target.value })}
          >
            {["telegram", "eitaa", "bale", "rubika", "whatsapp"].map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <input
            type="number"
            className="border rounded px-3 py-2 w-36"
            placeholder="حداکثر پیام/روز"
            value={form.rate_limit_per_day}
            onChange={(e) => setForm({ ...form, rate_limit_per_day: e.target.value })}
            min={1}
          />
          <input
            type="datetime-local"
            className="border rounded px-3 py-2"
            value={form.scheduled_at}
            onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
          />
        </div>
        <textarea
          className="border rounded px-3 py-2 w-full"
          rows={3}
          placeholder="متن پیام کمپین..."
          value={form.content}
          onChange={(e) => setForm({ ...form, content: e.target.value })}
          required
        />
        <div>
          <p className="font-medium mb-2 text-sm">انتخاب مخاطبین ({selectedIds.length} انتخاب شده):</p>
          <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
            {contacts.map((c) => (
              <label key={c.id} className="flex items-center gap-1 cursor-pointer bg-gray-100 px-2 py-1 rounded text-sm">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(c.id)}
                  onChange={() => toggleContact(c.id)}
                />
                {c.name}
              </label>
            ))}
          </div>
        </div>
        <button
          type="submit"
          disabled={creating}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          {creating ? "در حال ایجاد..." : "ایجاد و شروع کمپین"}
        </button>
      </form>

      <h3 className="text-lg font-semibold mb-3">کمپین‌ها</h3>
      <div className="space-y-3">
        {campaigns.map((c) => (
          <div key={c.id} className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{c.name}</span>
              <span className={`text-xs px-2 py-1 rounded ${STATUS_COLORS[c.status] || ""}`}>{c.status}</span>
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <p>پلتفرم: {c.platform} | گیرندگان: {c.total_recipients} | ارسال‌شده: {c.sent_count} | ناموفق: {c.failed_count}</p>
              <p className="truncate text-gray-500">{c.content}</p>
              {c.scheduled_at && <p>زمان‌بندی: {new Date(c.scheduled_at).toLocaleString("fa-IR")}</p>}
            </div>
            {/* Progress bar */}
            {c.total_recipients > 0 && (
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${(c.sent_count / c.total_recipients) * 100}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
