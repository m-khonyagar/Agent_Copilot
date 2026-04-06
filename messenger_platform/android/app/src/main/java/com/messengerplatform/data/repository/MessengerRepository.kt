package com.messengerplatform.data.repository

import com.messengerplatform.data.api.ApiClient
import com.messengerplatform.data.models.*

class MessengerRepository {

    private val api = ApiClient.service

    // ── Contacts ──────────────────────────────────────────────────────────────

    suspend fun getContacts() = runCatching { api.getContacts() }

    suspend fun createContact(name: String, phone: String, notes: String?) =
        runCatching { api.createContact(ContactCreate(name, phone, notes)) }

    suspend fun deleteContact(id: Int) = runCatching { api.deleteContact(id) }

    suspend fun checkAllPlatforms(id: Int) = runCatching { api.checkAllPlatforms(id) }

    // ── Messages ──────────────────────────────────────────────────────────────

    suspend fun getMessages(contactId: Int? = null, platform: String? = null, direction: String? = null) =
        runCatching { api.getMessages(contactId, platform, direction) }

    suspend fun sendMessage(contactId: Int, platform: String, content: String) =
        runCatching { api.sendSingle(SendSingleRequest(contactId, platform, content)) }

    suspend fun markRead(messageId: Int) = runCatching { api.markRead(messageId) }

    // ── Campaigns ─────────────────────────────────────────────────────────────

    suspend fun getCampaigns() = runCatching { api.getCampaigns() }

    suspend fun createCampaign(
        name: String,
        platform: String,
        content: String,
        contactIds: List<Int>,
        scheduledAt: String? = null,
        rateLimitPerDay: Int? = null
    ) = runCatching {
        api.createCampaign(CampaignCreate(name, platform, content, contactIds, scheduledAt, rateLimitPerDay))
    }

    // ── Admin ─────────────────────────────────────────────────────────────────

    suspend fun getDashboard() = runCatching { api.getDashboard() }

    suspend fun getNotifications(unreadOnly: Boolean = false) =
        runCatching { api.getNotifications(unreadOnly) }

    suspend fun markNotificationRead(id: Int) = runCatching { api.markNotificationRead(id) }

    suspend fun markAllNotificationsRead() = runCatching { api.markAllNotificationsRead() }

    suspend fun getInbox() = runCatching { api.getInbox() }

    suspend fun adminReply(messageId: Int, content: String) =
        runCatching { api.adminReply(AdminReplyRequest(messageId, content)) }

    suspend fun getContactHistory(contactId: Int) =
        runCatching { api.getContactHistory(contactId) }
}
