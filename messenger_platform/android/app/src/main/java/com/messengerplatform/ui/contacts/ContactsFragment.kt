package com.messengerplatform.ui.contacts

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.messengerplatform.databinding.FragmentContactsBinding
import com.messengerplatform.databinding.DialogAddContactBinding
import com.messengerplatform.viewmodel.MessengerViewModel

class ContactsFragment : Fragment() {

    private var _binding: FragmentContactsBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: MessengerViewModel
    private lateinit var adapter: ContactsAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentContactsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = ViewModelProvider(requireActivity())[MessengerViewModel::class.java]

        adapter = ContactsAdapter(
            onCheckPlatforms = { contact -> viewModel.checkAllPlatforms(contact.id) },
            onDelete = { contact -> viewModel.deleteContact(contact.id) }
        )
        binding.recyclerContacts.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerContacts.adapter = adapter

        viewModel.contacts.observe(viewLifecycleOwner) { adapter.submitList(it) }
        viewModel.contactsError.observe(viewLifecycleOwner) { Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show() }
        viewModel.loadContacts()

        binding.fabAddContact.setOnClickListener { showAddDialog() }

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadContacts()
            binding.swipeRefresh.isRefreshing = false
        }
    }

    private fun showAddDialog() {
        val dialogBinding = DialogAddContactBinding.inflate(layoutInflater)
        AlertDialog.Builder(requireContext())
            .setTitle("افزودن مخاطب")
            .setView(dialogBinding.root)
            .setPositiveButton("افزودن") { _, _ ->
                val name = dialogBinding.etName.text.toString().trim()
                val phone = dialogBinding.etPhone.text.toString().trim()
                val notes = dialogBinding.etNotes.text.toString().trim().ifEmpty { null }
                if (name.isNotEmpty() && phone.isNotEmpty()) {
                    viewModel.createContact(name, phone, notes)
                }
            }
            .setNegativeButton("لغو", null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
