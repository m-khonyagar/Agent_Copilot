import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Contacts from "./pages/Contacts";
import Messages from "./pages/Messages";
import Campaigns from "./pages/Campaigns";
import Inbox from "./pages/Inbox";
import History from "./pages/History";
import Notifications from "./pages/Notifications";
import {
  HomeIcon,
  UsersIcon,
  ChatBubbleLeftRightIcon,
  MegaphoneIcon,
  InboxIcon,
  ClockIcon,
  BellIcon,
} from "@heroicons/react/24/outline";

const navItems = [
  { to: "/", label: "داشبورد", Icon: HomeIcon },
  { to: "/contacts", label: "مخاطبین", Icon: UsersIcon },
  { to: "/messages", label: "پیام‌ها", Icon: ChatBubbleLeftRightIcon },
  { to: "/campaigns", label: "کمپین‌ها", Icon: MegaphoneIcon },
  { to: "/inbox", label: "صندوق دریافت", Icon: InboxIcon },
  { to: "/history", label: "تاریخچه", Icon: ClockIcon },
  { to: "/notifications", label: "اعلان‌ها", Icon: BellIcon },
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen" dir="rtl">
        {/* Sidebar */}
        <aside className="w-64 bg-blue-900 text-white flex flex-col py-6 px-4 gap-2 shrink-0">
          <h1 className="text-xl font-bold mb-6 px-2">📱 Messenger Platform</h1>
          {navItems.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive ? "bg-blue-700 font-semibold" : "hover:bg-blue-800"
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contacts" element={<Contacts />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/inbox" element={<Inbox />} />
            <Route path="/history" element={<History />} />
            <Route path="/notifications" element={<Notifications />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
