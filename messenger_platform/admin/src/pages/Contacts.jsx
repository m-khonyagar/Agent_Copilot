import React, { useEffect, useState } from "react";
import {
  getContacts,
  createContact,
  deleteContact,
  checkAllPlatforms,
} from "../api/client";

const PLATFORMS = ["telegram", "whatsapp", "eitaa", "bale", "rubika"];

const statusIcon = (val) => {
  if (val === true) return "✅";
  if (val === false) return "❌";
  return "❓";
};

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [form, setForm] = useState({ name: "", phone: "", notes: "" });
  const [loading, setLoading] = useState(false);
  const [checkingId, setCheckingId] = useState(null);

  const load = () =>
    getContacts().then((r) => setContacts(r.data)).catch(console.error);

  useEffect(() => { load(); }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createContact(form);
      setForm({ name: "", phone: "", notes: "" });
      await load();
    } catch (err) {
      alert(err?.response?.data?.detail || "خطا");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("حذف شود؟")) return;
    await deleteContact(id);
    await load();
  };

  const handleCheck = async (id) => {
    setCheckingId(id);
    try {
      await checkAllPlatforms(id);
      await load();
    } finally {
      setCheckingId(null);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">مخاطبین</h2>

      {/* Add form */}
      <form onSubmit={handleAdd} className="bg-white rounded-xl shadow p-4 mb-6 flex flex-wrap gap-3">
        <input
          className="border rounded px-3 py-2 flex-1 min-w-[150px]"
          placeholder="نام"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <input
          className="border rounded px-3 py-2 flex-1 min-w-[150px]"
          placeholder="شماره تلفن (مثال: +989123456789)"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          required
        />
        <input
          className="border rounded px-3 py-2 flex-1 min-w-[150px]"
          placeholder="یادداشت"
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          افزودن
        </button>
      </form>

      {/* Contacts table */}
      <div className="bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-4 py-3 text-right">نام</th>
              <th className="px-4 py-3 text-right">شماره</th>
              {PLATFORMS.map((p) => (
                <th key={p} className="px-3 py-3">{p}</th>
              ))}
              <th className="px-4 py-3">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {contacts.map((c) => {
              const platformMap = {};
              (c.platform_accounts || []).forEach((pa) => {
                platformMap[pa.platform] = pa;
              });
              return (
                <tr key={c.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">{c.name}</td>
                  <td className="px-4 py-3 font-mono">{c.phone}</td>
                  {PLATFORMS.map((p) => (
                    <td key={p} className="px-3 py-3 text-center">
                      <span title={platformMap[p]?.last_online || ""}>
                        {statusIcon(platformMap[p]?.has_account)}
                      </span>
                    </td>
                  ))}
                  <td className="px-4 py-3 flex gap-2 justify-center">
                    <button
                      onClick={() => handleCheck(c.id)}
                      disabled={checkingId === c.id}
                      className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                    >
                      {checkingId === c.id ? "..." : "بررسی پلتفرم‌ها"}
                    </button>
                    <button
                      onClick={() => handleDelete(c.id)}
                      className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200"
                    >
                      حذف
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
