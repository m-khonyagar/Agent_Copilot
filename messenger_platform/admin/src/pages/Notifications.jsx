import React, { useEffect, useState } from "react";
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
} from "../api/client";

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadOnly, setUnreadOnly] = useState(false);

  const load = (unread = unreadOnly) =>
    getNotifications(unread).then((r) => setNotifications(r.data)).catch(console.error);

  useEffect(() => { load(); }, [unreadOnly]);

  const handleRead = async (id) => {
    await markNotificationRead(id);
    load();
  };

  const handleReadAll = async () => {
    await markAllNotificationsRead();
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">اعلان‌ها</h2>
        <div className="flex gap-3 items-center">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
            />
            فقط خوانده‌نشده‌ها
          </label>
          <button
            onClick={handleReadAll}
            className="text-sm bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded"
          >
            همه را خوانده کن
          </button>
        </div>
      </div>

      {notifications.length === 0 && (
        <p className="text-gray-400">هیچ اعلانی وجود ندارد.</p>
      )}

      <div className="space-y-2">
        {notifications.map((n) => (
          <div
            key={n.id}
            className={`bg-white rounded-xl shadow p-4 flex items-start gap-3 ${
              !n.is_read ? "border-r-4 border-blue-500" : ""
            }`}
          >
            <div className="flex-1">
              <p className="font-semibold text-sm">{n.title}</p>
              <p className="text-sm text-gray-600 mt-1">{n.body}</p>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(n.created_at).toLocaleString("fa-IR")}
              </p>
            </div>
            {!n.is_read && (
              <button
                onClick={() => handleRead(n.id)}
                className="text-xs text-blue-600 hover:underline shrink-0"
              >
                خوانده شد
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
