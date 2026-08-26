package net.apperdashery.demo.ai_rag_android.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import net.apperdashery.demo.ai_rag_android.model.OshaStandardQuery
import net.apperdashery.demo.ai_rag_android.model.OshaStandardResponse
import net.apperdashery.demo.ai_rag_android.model.OshaValidationError
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

sealed class OshaApiException(message: String) : Exception(message) {
    class Server(val statusCode: Int, val userMessage: String) : OshaApiException(userMessage)
    class Transport(cause: Throwable) : OshaApiException(cause.message ?: "Network error")
    class Decoding(cause: Throwable) : OshaApiException("Couldn't read the server's response.")
}

interface OshaApiClient {
    suspend fun askOshaPPE(query: String): OshaStandardResponse
}

class OshaApiClientImpl(
    // 127.0.0.1 requires `adb reverse tcp:8000 tcp:8000` before launching the app.
    // (10.0.2.2, the emulator's usual host alias, was unreliable on this AVD image's
    // simulated Wi-Fi network — adb reverse tunnels over the adb transport instead
    // of the emulator's virtual NIC, so it isn't affected.)
    private val baseUrl: String = "http://127.0.0.1:8000",
    private val client: OkHttpClient = OkHttpClient(),
    private val json: Json = Json { ignoreUnknownKeys = true }
) : OshaApiClient {

    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    override suspend fun askOshaPPE(query: String): OshaStandardResponse = withContext(Dispatchers.IO) {
        val requestBody = json.encodeToString(
            OshaStandardQuery.serializer(),
            OshaStandardQuery(query = query)
        ).toRequestBody(jsonMediaType)

        val request = Request.Builder()
            .url("$baseUrl/v1/osha/ppe")
            .post(requestBody)
            .build()

        val response = try {
            client.newCall(request).execute()
        } catch (e: IOException) {
            throw OshaApiException.Transport(e)
        }

        response.use {
            val bodyString = it.body?.string().orEmpty()

            if (!it.isSuccessful) {
                val message = runCatching {
                    json.decodeFromString(OshaValidationError.serializer(), bodyString).detail
                }.getOrNull() ?: "Request failed with status ${it.code}."
                throw OshaApiException.Server(it.code, message)
            }

            try {
                json.decodeFromString(OshaStandardResponse.serializer(), bodyString)
            } catch (e: Exception) {
                throw OshaApiException.Decoding(e)
            }
        }
    }
}
