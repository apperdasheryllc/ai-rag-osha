package net.apperdashery.demo.ai_rag_android.store

import net.apperdashery.demo.ai_rag_android.model.OshaStandardResponse

sealed class AppAction {
    data class Osha(val action: OshaAction) : AppAction()
}

sealed class OshaAction {
    data class AskExpertTapped(val query: String) : OshaAction()
    data class ResponseReceived(val response: OshaStandardResponse) : OshaAction()
    data class RequestFailed(val message: String) : OshaAction()
    object DismissedResponse : OshaAction()
    object NavigationHandled : OshaAction()
}
