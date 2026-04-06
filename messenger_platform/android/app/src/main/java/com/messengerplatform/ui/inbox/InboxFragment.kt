package com.messengerplatform.ui.inbox

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.messengerplatform.databinding.FragmentInboxBinding
import com.messengerplatform.viewmodel.MessengerViewModel

class InboxFragment : Fragment() {

    private var _binding: FragmentInboxBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: MessengerViewModel
    private lateinit var adapter: InboxAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentInboxBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = ViewModelProvider(requireActivity())[MessengerViewModel::class.java]

        adapter = InboxAdapter { messageId, content ->
            viewModel.adminReply(messageId, content)
            Toast.makeText(requireContext(), "پاسخ ارسال شد", Toast.LENGTH_SHORT).show()
        }
        binding.recyclerInbox.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerInbox.adapter = adapter

        viewModel.inbox.observe(viewLifecycleOwner) { messages ->
            adapter.submitList(messages)
            binding.tvEmpty.visibility = if (messages.isEmpty()) View.VISIBLE else View.GONE
        }
        viewModel.loadInbox()

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadInbox()
            binding.swipeRefresh.isRefreshing = false
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
