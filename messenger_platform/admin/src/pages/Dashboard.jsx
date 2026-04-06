import React, { useEffect, useState } from "react";
import { getDashboard } from "../api/client";

const StatCard = ({ label, value, color }) => (
  <div className={`rounded-xl p-5 text-white ${color}`}>
    <p className="text-sm opacity-80">{label}</p>
    <p className="text-3xl font-bold mt-1">{value ?? "..."}</p>
  </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboard()
      .then((r) => setStats(r.data))
      .catch(() => setError("خطا در دریافت اطلاعات"));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">داشبورد</h2>
      {error && <p className="text-red-500">{error}</p>}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatCard label="کل مخاطبین" value={stats.total_contacts} color="bg-blue-600" />
          <StatCard label="پیام‌های ارسالی" value={stats.total_messages_sent} color="bg-green-600" />
          <StatCard label="پیام‌های خوانده‌شده" value={stats.total_messages_read} color="bg-teal-600" />
          <StatCard label="پیام‌های دریافتی" value={stats.total_inbound} color="bg-purple-600" />
          <StatCard label="کمپین‌های فعال" value={stats.active_campaigns} color="bg-orange-500" />
          <StatCard label="اعلان‌های خوانده‌نشده" value={stats.unread_notifications} color="bg-red-500" />
        </div>
      )}
    </div>
  );
}
