package net.apperdashery.demo.ai_rag_android.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class OshaStandardQuery(
    val query: String,
    val results: Int = 5
)

@Serializable
data class OshaStandardResponse(
    val answer: String,
    val sources: List<OshaSource>
)

@Serializable
data class OshaSource(
    val citation: String,
    val label: String,
    @SerialName("source_url") val sourceUrl: String,
    val text: String
)

@Serializable
data class OshaValidationError(
    val detail: String
)
