package com.messengerplatform.ui.inbox

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.messengerplatform.data.models.InboxMessage
import com.messengerplatform.databinding.ItemInboxBinding

class InboxAdapter(
    private val onReply: (messageId: Int, content: String) -> Unit
) : ListAdapter<InboxMessage, InboxAdapter.ViewHolder>(DIFF_CALLBACK) {

    inner class ViewHolder(private val binding: ItemInboxBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(msg: InboxMessage) {
            binding.tvSender.text = "${msg.contactName} (${msg.contactPhone})"
            binding.tvPlatform.text = msg.platform
            binding.tvContent.text = msg.content
            binding.tvTime.text = msg.createdAt

            binding.btnReply.setOnClickListener {
                val replyText = binding.etReply.text.toString().trim()
                if (replyText.isNotEmpty()) {
                    onReply(msg.id, replyText)
                    binding.etReply.text?.clear()
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemInboxBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) = holder.bind(getItem(position))

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<InboxMessage>() {
            override fun areItemsTheSame(old: InboxMessage, new: InboxMessage) = old.id == new.id
            override fun areContentsTheSame(old: InboxMessage, new: InboxMessage) = old == new
        }
    }
}
