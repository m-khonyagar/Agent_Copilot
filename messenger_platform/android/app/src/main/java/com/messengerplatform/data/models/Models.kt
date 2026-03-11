package com.messengerplatform.data.models

import com.google.gson.annotations.SerializedName

// ── Contact ───────────────────────────────────────────────────────────────────

data class Contact(
    val id: Int,
    val name: String,
    val phone: String,
    val notes: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("platform_accounts") val platformAccounts: List<PlatformAccount> = emptyList()
)

data class PlatformAccount(
    val platform: String,
    @SerializedName("has_account") val hasAccount: Boolean?,
    val username: String?,
    @SerializedName("last_online") val lastOnline: String?,
    @SerializedName("last_checked") val lastChecked: String?
)

data class ContactCreate(
    val name: String,
    val phone: String,
    val notes: String? = null
)

// ── Message ───────────────────────────────────────────────────────────────────

data class Message(
    val id: Int,
    @SerializedName("contact_id") val contactId: Int,
    val platform: String,
    val direction: String,
    val content: String,
    val status: String,
    @SerializedName("platform_message_id") val platformMessageId: String?,
    @SerializedName("sent_at") val sentAt: String?,
    @SerializedName("read_at") val readAt: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("contact_name") val contactName: String?,
    @SerializedName("contact_phone") val contactPhone: String?
)

data class SendSingleRequest(
    @SerializedName("contact_id") val contactId: Int,
    val platform: String,
    val content: String
)

// ── Campaign ──────────────────────────────────────────────────────────────────

data class Campaign(
    val id: Int,
    val name: String,
    val platform: String,
    val content: String,
    val status: String,
    @SerializedName("total_recipients") val totalRecipients: Int,
    @SerializedName("sent_count") val sentCount: Int,
    @SerializedName("failed_count") val failedCount: Int,
    @SerializedName("scheduled_at") val scheduledAt: String?,
    @SerializedName("created_at") val createdAt: String
)

data class CampaignCreate(
    val name: String,
    val platform: String,
    val content: String,
    @SerializedName("contact_ids") val contactIds: List<Int>,
    @SerializedName("scheduled_at") val scheduledAt: String? = null,
    @SerializedName("rate_limit_per_day") val rateLimitPerDay: Int? = null
)

// ── Admin ─────────────────────────────────────────────────────────────────────

data class DashboardStats(
    @SerializedName("total_contacts") val totalContacts: Int,
    @SerializedName("total_messages_sent") val totalMessagesSent: Int,
    @SerializedName("total_messages_read") val totalMessagesRead: Int,
    @SerializedName("total_inbound") val totalInbound: Int,
    @SerializedName("active_campaigns") val activeCampaigns: Int,
    @SerializedName("unread_notifications") val unreadNotifications: Int
)

data class Notification(
    val id: Int,
    val title: String,
    val body: String,
    @SerializedName("is_read") val isRead: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("related_message_id") val relatedMessageId: Int?,
    @SerializedName("related_contact_id") val relatedContactId: Int?
)

data class InboxMessage(
    val id: Int,
    @SerializedName("contact_id") val contactId: Int,
    @SerializedName("contact_name") val contactName: String,
    @SerializedName("contact_phone") val contactPhone: String,
    val platform: String,
    val content: String,
    @SerializedName("created_at") val createdAt: String,
    val status: String
)

data class AdminReplyRequest(
    @SerializedName("message_id") val messageId: Int,
    val content: String
)
