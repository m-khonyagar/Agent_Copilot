package com.messengerplatform.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.messengerplatform.data.models.*
import com.messengerplatform.data.repository.MessengerRepository
import kotlinx.coroutines.launch

class MessengerViewModel : ViewModel() {

    private val repository = MessengerRepository()

    // ── Contacts ──────────────────────────────────────────────────────────────

    private val _contacts = MutableLiveData<List<Contact>>()
    val contacts: LiveData<List<Contact>> = _contacts

    private val _contactsError = MutableLiveData<String>()
    val contactsError: LiveData<String> = _contactsError

    fun loadContacts() {
        viewModelScope.launch {
            repository.getContacts().fold(
                onSuccess = { _contacts.value = it },
                onFailure = { _contactsError.value = it.message }
            )
        }
    }

    fun createContact(name: String, phone: String, notes: String?) {
        viewModelScope.launch {
            repository.createContact(name, phone, notes).fold(
                onSuccess = { loadContacts() },
                onFailure = { _contactsError.value = it.message }
            )
        }
    }

    fun deleteContact(id: Int) {
        viewModelScope.launch {
            repository.deleteContact(id).fold(
                onSuccess = { loadContacts() },
                onFailure = { _contactsError.value = it.message }
            )
        }
    }

    fun checkAllPlatforms(id: Int) {
        viewModelScope.launch {
            repository.checkAllPlatforms(id).fold(
                onSuccess = { loadContacts() },
                onFailure = { _contactsError.value = it.message }
            )
        }
    }

    // ── Messages ──────────────────────────────────────────────────────────────

    private val _messages = MutableLiveData<List<Message>>()
    val messages: LiveData<List<Message>> = _messages

    private val _messagesError = MutableLiveData<String>()
    val messagesError: LiveData<String> = _messagesError

    private val _sendSuccess = MutableLiveData<Boolean>()
    val sendSuccess: LiveData<Boolean> = _sendSuccess

    fun loadMessages(contactId: Int? = null, platform: String? = null, direction: String? = null) {
        viewModelScope.launch {
            repository.getMessages(contactId, platform, direction).fold(
                onSuccess = { _messages.value = it },
                onFailure = { _messagesError.value = it.message }
            )
        }
    }

    fun sendMessage(contactId: Int, platform: String, content: String) {
        viewModelScope.launch {
            repository.sendMessage(contactId, platform, content).fold(
                onSuccess = {
                    _sendSuccess.value = true
                    loadMessages()
                },
                onFailure = { _messagesError.value = it.message }
            )
        }
    }

    // ── Campaigns ─────────────────────────────────────────────────────────────

    private val _campaigns = MutableLiveData<List<Campaign>>()
    val campaigns: LiveData<List<Campaign>> = _campaigns

    fun loadCampaigns() {
        viewModelScope.launch {
            repository.getCampaigns().fold(
                onSuccess = { _campaigns.value = it },
                onFailure = { /* no-op */ }
            )
        }
    }

    fun createCampaign(
        name: String,
        platform: String,
        content: String,
        contactIds: List<Int>,
        scheduledAt: String? = null,
        rateLimitPerDay: Int? = null
    ) {
        viewModelScope.launch {
            repository.createCampaign(name, platform, content, contactIds, scheduledAt, rateLimitPerDay).fold(
                onSuccess = { loadCampaigns() },
                onFailure = { /* handle error */ }
            )
        }
    }

    // ── Admin / Notifications ─────────────────────────────────────────────────

    private val _dashboard = MutableLiveData<DashboardStats>()
    val dashboard: LiveData<DashboardStats> = _dashboard

    private val _notifications = MutableLiveData<List<Notification>>()
    val notifications: LiveData<List<Notification>> = _notifications

    private val _inbox = MutableLiveData<List<InboxMessage>>()
    val inbox: LiveData<List<InboxMessage>> = _inbox

    fun loadDashboard() {
        viewModelScope.launch {
            repository.getDashboard().onSuccess { _dashboard.value = it }
        }
    }

    fun loadNotifications(unreadOnly: Boolean = false) {
        viewModelScope.launch {
            repository.getNotifications(unreadOnly).onSuccess { _notifications.value = it }
        }
    }

    fun markNotificationRead(id: Int) {
        viewModelScope.launch {
            repository.markNotificationRead(id).onSuccess { loadNotifications() }
        }
    }

    fun markAllNotificationsRead() {
        viewModelScope.launch {
            repository.markAllNotificationsRead().onSuccess { loadNotifications() }
        }
    }

    fun loadInbox() {
        viewModelScope.launch {
            repository.getInbox().onSuccess { _inbox.value = it }
        }
    }

    fun adminReply(messageId: Int, content: String) {
        viewModelScope.launch {
            repository.adminReply(messageId, content).onSuccess { loadInbox() }
        }
    }

    // ── History ───────────────────────────────────────────────────────────────

    private val _history = MutableLiveData<List<Map<String, Any>>>()
    val history: LiveData<List<Map<String, Any>>> = _history

    fun loadHistory(contactId: Int) {
        viewModelScope.launch {
            repository.getContactHistory(contactId).onSuccess { _history.value = it }
        }
    }
}
