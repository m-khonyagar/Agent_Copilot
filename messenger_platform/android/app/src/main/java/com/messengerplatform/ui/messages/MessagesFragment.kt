package com.messengerplatform.ui.messages

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.messengerplatform.R
import com.messengerplatform.databinding.FragmentMessagesBinding
import com.messengerplatform.viewmodel.MessengerViewModel

class MessagesFragment : Fragment() {

    private var _binding: FragmentMessagesBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: MessengerViewModel
    private lateinit var adapter: MessagesAdapter
    private val platforms = listOf("telegram", "eitaa", "bale", "rubika", "whatsapp")

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentMessagesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = ViewModelProvider(requireActivity())[MessengerViewModel::class.java]

        // Platform spinner
        binding.spinnerPlatform.adapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_spinner_dropdown_item,
            platforms
        )

        // Messages list
        adapter = MessagesAdapter()
        binding.recyclerMessages.layoutManager = LinearLayoutManager(requireContext()).apply {
            stackFromEnd = true
        }
        binding.recyclerMessages.adapter = adapter

        viewModel.messages.observe(viewLifecycleOwner) {
            adapter.submitList(it)
            binding.recyclerMessages.scrollToPosition(it.size - 1)
        }
        viewModel.messagesError.observe(viewLifecycleOwner) {
            Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
        }
        viewModel.sendSuccess.observe(viewLifecycleOwner) {
            if (it == true) binding.etContent.text?.clear()
        }

        viewModel.loadMessages()
        viewModel.loadContacts()

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadMessages()
            binding.swipeRefresh.isRefreshing = false
        }

        binding.btnSend.setOnClickListener {
            val contactId = getSelectedContactId() ?: run {
                Toast.makeText(requireContext(), "مخاطبی انتخاب نشده", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val platform = platforms[binding.spinnerPlatform.selectedItemPosition]
            val content = binding.etContent.text?.toString()?.trim() ?: ""
            if (content.isEmpty()) {
                Toast.makeText(requireContext(), "متن پیام خالی است", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            viewModel.sendMessage(contactId, platform, content)
        }
    }

    private fun getSelectedContactId(): Int? {
        val contacts = viewModel.contacts.value ?: return null
        val position = binding.spinnerContact.selectedItemPosition
        return contacts.getOrNull(position)?.id
    }

    override fun onResume() {
        super.onResume()
        // Populate contact spinner when fragment resumes (contacts may have loaded)
        viewModel.contacts.observe(viewLifecycleOwner) { contacts ->
            val names = contacts.map { "${it.name} (${it.phone})" }
            binding.spinnerContact.adapter = ArrayAdapter(
                requireContext(),
                android.R.layout.simple_spinner_dropdown_item,
                names
            )
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
