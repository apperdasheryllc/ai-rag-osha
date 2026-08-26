package net.apperdashery.demo.ai_rag_android.store

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import net.apperdashery.demo.ai_rag_android.network.OshaApiClient
import net.apperdashery.demo.ai_rag_android.network.OshaApiClientImpl
import net.apperdashery.demo.ai_rag_android.network.OshaApiException
import java.util.concurrent.Executors

class AppStore(
    private val oshaClient: OshaApiClient = OshaApiClientImpl(),
    private val storeScope: CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
) {
    private val reducerDispatcher = Executors.newSingleThreadExecutor().asCoroutineDispatcher()

    private val _state = MutableStateFlow(AppState())
    val state: StateFlow<AppState> = _state.asStateFlow()

    fun dispatch(action: AppAction) {
        val currentState = _state.value
        storeScope.launch(reducerDispatcher) {
            val newState = appReducer(currentState, action)
            _state.value = newState
            runEffect(action)
        }
    }

    private fun runEffect(action: AppAction) {
        val askExpertAction = (action as? AppAction.Osha)?.action as? OshaAction.AskExpertTapped ?: return
        storeScope.launch {
            try {
                val response = oshaClient.askOshaPPE(askExpertAction.query)
                dispatch(AppAction.Osha(OshaAction.ResponseReceived(response)))
            } catch (e: OshaApiException) {
                dispatch(AppAction.Osha(OshaAction.RequestFailed(e.message ?: "Something went wrong.")))
            }
        }
    }
}
