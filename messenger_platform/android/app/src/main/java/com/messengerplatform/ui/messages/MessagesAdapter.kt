package com.messengerplatform.ui.messages

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.messengerplatform.data.models.Message
import com.messengerplatform.databinding.ItemMessageOutboundBinding
import com.messengerplatform.databinding.ItemMessageInboundBinding

private const val VIEW_TYPE_OUTBOUND = 0
private const val VIEW_TYPE_INBOUND = 1

class MessagesAdapter : ListAdapter<Message, RecyclerView.ViewHolder>(DIFF_CALLBACK) {

    override fun getItemViewType(position: Int) =
        if (getItem(position).direction == "outbound") VIEW_TYPE_OUTBOUND else VIEW_TYPE_INBOUND

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return if (viewType == VIEW_TYPE_OUTBOUND) {
            OutboundViewHolder(
                ItemMessageOutboundBinding.inflate(LayoutInflater.from(parent.context), parent, false)
            )
        } else {
            InboundViewHolder(
                ItemMessageInboundBinding.inflate(LayoutInflater.from(parent.context), parent, false)
            )
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val msg = getItem(position)
        when (holder) {
            is OutboundViewHolder -> holder.bind(msg)
            is InboundViewHolder -> holder.bind(msg)
        }
    }

    inner class OutboundViewHolder(private val binding: ItemMessageOutboundBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(msg: Message) {
            binding.tvContent.text = msg.content
            binding.tvPlatform.text = msg.platform
            binding.tvStatus.text = when (msg.status) {
                "read" -> "✓✓ خوانده شد"
                "delivered" -> "✓✓"
                "sent" -> "✓"
                "failed" -> "✗"
                else -> "⏳"
            }
            binding.tvTime.text = msg.sentAt ?: msg.createdAt
        }
    }

    inner class InboundViewHolder(private val binding: ItemMessageInboundBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(msg: Message) {
            binding.tvContent.text = msg.content
            binding.tvSender.text = msg.contactName ?: msg.contactPhone ?: ""
            binding.tvPlatform.text = msg.platform
            binding.tvTime.text = msg.createdAt
        }
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Message>() {
            override fun areItemsTheSame(old: Message, new: Message) = old.id == new.id
            override fun areContentsTheSame(old: Message, new: Message) = old == new
        }
    }
}
