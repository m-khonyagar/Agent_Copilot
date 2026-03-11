package com.messengerplatform.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.badge.BadgeDrawable
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.messengerplatform.R
import com.messengerplatform.databinding.ActivityMainBinding
import com.messengerplatform.service.NotificationListenerService
import com.messengerplatform.viewmodel.MessengerViewModel

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MessengerViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this)[MessengerViewModel::class.java]

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
        binding.bottomNav.setupWithNavController(navController)

        // Observe unread notification count for badge
        viewModel.loadNotifications(unreadOnly = true)
        viewModel.notifications.observe(this) { notifications ->
            val badge = binding.bottomNav.getOrCreateBadge(R.id.nav_notifications)
            if (notifications.isNotEmpty()) {
                badge.isVisible = true
                badge.number = notifications.size
            } else {
                badge.isVisible = false
            }
        }

        // Start background notification polling service
        startService(Intent(this, NotificationListenerService::class.java))
    }
}
