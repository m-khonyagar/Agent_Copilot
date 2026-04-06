package com.messengerplatform.ui.contacts

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.messengerplatform.data.models.Contact
import com.messengerplatform.databinding.ItemContactBinding

class ContactsAdapter(
    private val onCheckPlatforms: (Contact) -> Unit,
    private val onDelete: (Contact) -> Unit
) : ListAdapter<Contact, ContactsAdapter.ViewHolder>(DIFF_CALLBACK) {

    inner class ViewHolder(private val binding: ItemContactBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(contact: Contact) {
            binding.tvName.text = contact.name
            binding.tvPhone.text = contact.phone

            // Build platform status summary
            val platformMap = contact.platformAccounts.associateBy { it.platform }
            val platforms = listOf("telegram", "whatsapp", "eitaa", "bale", "rubika")
            val statusText = platforms.joinToString("  ") { p ->
                val account = platformMap[p]
                val icon = when (account?.hasAccount) {
                    true -> "✅"
                    false -> "❌"
                    null -> "❓"
                }
                "${p.take(3).uppercase()}:$icon"
            }
            binding.tvPlatformStatus.text = statusText

            // Last online (from telegram if available)
            val telegramAccount = platformMap["telegram"]
            binding.tvLastOnline.text = telegramAccount?.lastOnline?.let {
                "آخرین آنلاین: $it"
            } ?: ""

            binding.btnCheckPlatforms.setOnClickListener { onCheckPlatforms(contact) }
            binding.btnDelete.setOnClickListener { onDelete(contact) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemContactBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Contact>() {
            override fun areItemsTheSame(old: Contact, new: Contact) = old.id == new.id
            override fun areContentsTheSame(old: Contact, new: Contact) = old == new
        }
    }
}
