package net.apperdashery.demo.ai_rag_android.store

import net.apperdashery.demo.ai_rag_android.model.OshaStandardResponse

data class AppState(
    val osha: OshaState = OshaState()
)

data class OshaState(
    val isLoading: Boolean = false,
    val response: OshaStandardResponse? = null,
    val errorMessage: String? = null,
    val route: OshaRoute? = null
)

enum class OshaRoute {
    Response
}
