import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// ── Contacts ──────────────────────────────────────────────────────────────────
export const getContacts = () => api.get("/contacts");
export const createContact = (data) => api.post("/contacts", data);
export const updateContact = (id, data) => api.patch(`/contacts/${id}`, data);
export const deleteContact = (id) => api.delete(`/contacts/${id}`);
export const checkAllPlatforms = (id) => api.post(`/contacts/${id}/check-platforms`);
export const checkPlatform = (id, platform) => api.post(`/contacts/${id}/check-platform/${platform}`);

// ── Messages ──────────────────────────────────────────────────────────────────
export const getMessages = (params) => api.get("/messages", { params });
export const sendSingle = (data) => api.post("/messages/send", data);
export const markRead = (id) => api.post(`/messages/${id}/mark-read`);
export const receiveInbound = (params) => api.post("/messages/inbound", null, { params });

// ── Campaigns ─────────────────────────────────────────────────────────────────
export const getCampaigns = () => api.get("/messages/campaigns");
export const createCampaign = (data) => api.post("/messages/campaigns", data);
export const getCampaign = (id) => api.get(`/messages/campaigns/${id}`);

// ── Admin ─────────────────────────────────────────────────────────────────────
export const getDashboard = () => api.get("/admin/dashboard");
export const getNotifications = (unread) => api.get("/admin/notifications", { params: { unread_only: unread } });
export const markNotificationRead = (id) => api.post(`/admin/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.post("/admin/notifications/read-all");
export const getInbox = () => api.get("/admin/inbox");
export const adminReply = (data) => api.post("/admin/reply", data);
export const getContactHistory = (id) => api.get(`/admin/history/${id}`);
