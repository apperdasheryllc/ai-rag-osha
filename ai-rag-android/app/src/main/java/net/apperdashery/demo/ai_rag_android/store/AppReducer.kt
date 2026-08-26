package net.apperdashery.demo.ai_rag_android.store

fun appReducer(state: AppState, action: AppAction): AppState =
    when (action) {
        is AppAction.Osha -> state.copy(osha = oshaReducer(state.osha, action.action))
    }

fun oshaReducer(state: OshaState, action: OshaAction): OshaState =
    when (action) {
        is OshaAction.AskExpertTapped -> state.copy(
            isLoading = true,
            response = null,
            errorMessage = null
        )

        is OshaAction.ResponseReceived -> state.copy(
            isLoading = false,
            response = action.response,
            errorMessage = null,
            route = OshaRoute.Response
        )

        is OshaAction.RequestFailed -> state.copy(
            isLoading = false,
            response = null,
            errorMessage = action.message,
            route = OshaRoute.Response
        )

        is OshaAction.DismissedResponse -> state.copy(
            response = null,
            errorMessage = null,
            route = null
        )

        is OshaAction.NavigationHandled -> state.copy(route = null)
    }
