package com.messengerplatform.ui.history

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.messengerplatform.databinding.ItemMessageInboundBinding
import com.messengerplatform.databinding.ItemMessageOutboundBinding

private const val VIEW_TYPE_OUTBOUND = 0
private const val VIEW_TYPE_INBOUND = 1

class HistoryAdapter : ListAdapter<Map<String, Any>, RecyclerView.ViewHolder>(DIFF_CALLBACK) {

    override fun getItemViewType(position: Int) =
        if (getItem(position)["direction"] == "outbound") VIEW_TYPE_OUTBOUND else VIEW_TYPE_INBOUND

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return if (viewType == VIEW_TYPE_OUTBOUND) {
            OutboundVH(ItemMessageOutboundBinding.inflate(LayoutInflater.from(parent.context), parent, false))
        } else {
            InboundVH(ItemMessageInboundBinding.inflate(LayoutInflater.from(parent.context), parent, false))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item = getItem(position)
        when (holder) {
            is OutboundVH -> holder.bind(item)
            is InboundVH -> holder.bind(item)
        }
    }

    inner class OutboundVH(private val b: ItemMessageOutboundBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(item: Map<String, Any>) {
            b.tvContent.text = item["content"] as? String ?: ""
            b.tvPlatform.text = item["platform"] as? String ?: ""
            val status = item["status"] as? String ?: ""
            b.tvStatus.text = when (status) {
                "read" -> "✓✓ خوانده شد"
                "delivered" -> "✓✓"
                "sent" -> "✓"
                "failed" -> "✗"
                else -> "⏳"
            }
            b.tvTime.text = (item["read_at"] as? String) ?: (item["sent_at"] as? String) ?: (item["created_at"] as? String) ?: ""
        }
    }

    inner class InboundVH(private val b: ItemMessageInboundBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(item: Map<String, Any>) {
            b.tvContent.text = item["content"] as? String ?: ""
            b.tvSender.text = "کاربر"
            b.tvPlatform.text = item["platform"] as? String ?: ""
            b.tvTime.text = item["created_at"] as? String ?: ""
        }
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Map<String, Any>>() {
            override fun areItemsTheSame(old: Map<String, Any>, new: Map<String, Any>) = old["id"] == new["id"]
            override fun areContentsTheSame(old: Map<String, Any>, new: Map<String, Any>) = old == new
        }
    }
}
