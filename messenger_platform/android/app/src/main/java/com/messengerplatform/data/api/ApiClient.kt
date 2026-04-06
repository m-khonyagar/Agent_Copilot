package com.messengerplatform.data.api

import com.messengerplatform.BuildConfig
import com.messengerplatform.data.models.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

interface MessengerApiService {

    // ── Contacts ──────────────────────────────────────────────────────────────

    @GET("contacts")
    suspend fun getContacts(): List<Contact>

    @POST("contacts")
    suspend fun createContact(@Body data: ContactCreate): Contact

    @DELETE("contacts/{id}")
    suspend fun deleteContact(@Path("id") id: Int): Response<Unit>

    @POST("contacts/{id}/check-platforms")
    suspend fun checkAllPlatforms(@Path("id") id: Int): List<PlatformAccount>

    @POST("contacts/{id}/check-platform/{platform}")
    suspend fun checkPlatform(
        @Path("id") id: Int,
        @Path("platform") platform: String
    ): PlatformAccount

    // ── Messages ──────────────────────────────────────────────────────────────

    @GET("messages")
    suspend fun getMessages(
        @Query("contact_id") contactId: Int? = null,
        @Query("platform") platform: String? = null,
        @Query("direction") direction: String? = null
    ): List<Message>

    @POST("messages/send")
    suspend fun sendSingle(@Body data: SendSingleRequest): Message

    @POST("messages/{id}/mark-read")
    suspend fun markRead(@Path("id") id: Int): Message

    @POST("messages/inbound")
    suspend fun receiveInbound(
        @Query("contact_id") contactId: Int,
        @Query("platform") platform: String,
        @Query("content") content: String,
        @Query("platform_message_id") platformMessageId: String? = null
    ): Message

    // ── Campaigns ─────────────────────────────────────────────────────────────

    @GET("messages/campaigns")
    suspend fun getCampaigns(): List<Campaign>

    @POST("messages/campaigns")
    suspend fun createCampaign(@Body data: CampaignCreate): Campaign

    // ── Admin ─────────────────────────────────────────────────────────────────

    @GET("admin/dashboard")
    suspend fun getDashboard(): DashboardStats

    @GET("admin/notifications")
    suspend fun getNotifications(@Query("unread_only") unreadOnly: Boolean = false): List<Notification>

    @POST("admin/notifications/{id}/read")
    suspend fun markNotificationRead(@Path("id") id: Int): Notification

    @POST("admin/notifications/read-all")
    suspend fun markAllNotificationsRead(): Response<Unit>

    @GET("admin/inbox")
    suspend fun getInbox(): List<InboxMessage>

    @POST("admin/reply")
    suspend fun adminReply(@Body data: AdminReplyRequest): Map<String, Any>

    @GET("admin/history/{contactId}")
    suspend fun getContactHistory(@Path("contactId") contactId: Int): List<Map<String, Any>>
}

object ApiClient {

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()

    val service: MessengerApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL + "/")
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(MessengerApiService::class.java)
    }
}
