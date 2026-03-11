package com.messengerplatform

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

class MessengerApp : Application() {

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)

            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_MESSAGES,
                    "پیام‌های جدید",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply { description = "اعلان پیام‌های دریافتی جدید" }
            )

            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_CAMPAIGNS,
                    "وضعیت کمپین",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply { description = "اعلان وضعیت کمپین‌های ارسال پیام" }
            )
        }
    }

    companion object {
        const val CHANNEL_MESSAGES = "channel_messages"
        const val CHANNEL_CAMPAIGNS = "channel_campaigns"
    }
}
