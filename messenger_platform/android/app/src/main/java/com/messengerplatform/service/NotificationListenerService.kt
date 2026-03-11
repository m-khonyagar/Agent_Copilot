package com.messengerplatform.service

import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.messengerplatform.MessengerApp
import com.messengerplatform.R
import com.messengerplatform.data.repository.MessengerRepository
import com.messengerplatform.ui.MainActivity
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Background service that polls the backend for unread notifications every
 * 60 seconds and surfaces them as Android system notifications.
 */
class NotificationListenerService : LifecycleService() {

    private val repository = MessengerRepository()
    private var lastSeenNotificationId = -1

    override fun onCreate() {
        super.onCreate()
        lifecycleScope.launch {
            while (true) {
                try {
                    pollNotifications()
                } catch (_: Exception) { }
                delay(60_000)
            }
        }
    }

    private suspend fun pollNotifications() {
        repository.getNotifications(unreadOnly = true).onSuccess { notifications ->
            notifications
                .filter { it.id > lastSeenNotificationId }
                .forEach { notif ->
                    showNotification(notif.id, notif.title, notif.body)
                    if (notif.id > lastSeenNotificationId) lastSeenNotificationId = notif.id
                }
        }
    }

    private fun showNotification(id: Int, title: String, body: String) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE)

        val notification = NotificationCompat.Builder(this, MessengerApp.CHANNEL_MESSAGES)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .build()

        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(id, notification)
    }
}
