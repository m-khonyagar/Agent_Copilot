package com.messengerplatform.ui.history

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.messengerplatform.databinding.FragmentHistoryBinding
import com.messengerplatform.viewmodel.MessengerViewModel

class HistoryFragment : Fragment() {

    private var _binding: FragmentHistoryBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: MessengerViewModel
    private lateinit var adapter: HistoryAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentHistoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = ViewModelProvider(requireActivity())[MessengerViewModel::class.java]

        adapter = HistoryAdapter()
        binding.recyclerHistory.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerHistory.adapter = adapter

        viewModel.contacts.observe(viewLifecycleOwner) { contacts ->
            val names = contacts.map { "${it.name} (${it.phone})" }
            binding.spinnerContact.adapter = ArrayAdapter(
                requireContext(),
                android.R.layout.simple_spinner_dropdown_item,
                names
            )
        }

        viewModel.history.observe(viewLifecycleOwner) { history ->
            adapter.submitList(history)
        }

        viewModel.loadContacts()

        binding.btnLoad.setOnClickListener {
            val contacts = viewModel.contacts.value ?: return@setOnClickListener
            val contact = contacts.getOrNull(binding.spinnerContact.selectedItemPosition)
                ?: return@setOnClickListener
            viewModel.loadHistory(contact.id)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
