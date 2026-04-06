package com.messengerplatform.ui.notifications

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.messengerplatform.data.models.Notification
import com.messengerplatform.databinding.ItemNotificationBinding

class NotificationsAdapter(
    private val onMarkRead: (Int) -> Unit
) : ListAdapter<Notification, NotificationsAdapter.ViewHolder>(DIFF_CALLBACK) {

    inner class ViewHolder(private val binding: ItemNotificationBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(notif: Notification) {
            binding.tvTitle.text = notif.title
            binding.tvBody.text = notif.body
            binding.tvTime.text = notif.createdAt
            if (!notif.isRead) {
                binding.root.alpha = 1f
                binding.btnMarkRead.visibility = android.view.View.VISIBLE
                binding.btnMarkRead.setOnClickListener { onMarkRead(notif.id) }
            } else {
                binding.root.alpha = 0.6f
                binding.btnMarkRead.visibility = android.view.View.GONE
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemNotificationBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) = holder.bind(getItem(position))

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Notification>() {
            override fun areItemsTheSame(old: Notification, new: Notification) = old.id == new.id
            override fun areContentsTheSame(old: Notification, new: Notification) = old == new
        }
    }
}
