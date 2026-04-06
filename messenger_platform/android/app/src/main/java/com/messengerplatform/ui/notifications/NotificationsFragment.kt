package com.messengerplatform.ui.notifications

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.messengerplatform.databinding.FragmentNotificationsBinding
import com.messengerplatform.viewmodel.MessengerViewModel

class NotificationsFragment : Fragment() {

    private var _binding: FragmentNotificationsBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: MessengerViewModel
    private lateinit var adapter: NotificationsAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentNotificationsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = ViewModelProvider(requireActivity())[MessengerViewModel::class.java]

        adapter = NotificationsAdapter { id ->
            viewModel.markNotificationRead(id)
        }
        binding.recyclerNotifications.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerNotifications.adapter = adapter

        viewModel.notifications.observe(viewLifecycleOwner) { notifications ->
            adapter.submitList(notifications)
            binding.tvEmpty.visibility = if (notifications.isEmpty()) View.VISIBLE else View.GONE
        }
        viewModel.loadNotifications()

        binding.btnMarkAll.setOnClickListener {
            viewModel.markAllNotificationsRead()
        }

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadNotifications()
            binding.swipeRefresh.isRefreshing = false
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
