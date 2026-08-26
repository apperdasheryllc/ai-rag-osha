//
//  AppReducer.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Foundation

func appReducer(_ state: AppState, _ action: AppAction) -> AppState {
    var newState = state
    switch action {
    case .osha(let oshaAction):
        newState.osha = oshaReducer(state.osha, oshaAction)
    }
    return newState
}

func oshaReducer(_ state: OshaState, _ action: OshaAction) -> OshaState {
    var newState = state
    switch action {
    case .askExpertTapped:
        newState.isLoading = true
        newState.response = nil
        newState.errorMessage = nil

    case .responseReceived(let response):
        newState.isLoading = false
        newState.response = response
        newState.errorMessage = nil
        newState.route = [.response]

    case .requestFailed(let message):
        newState.isLoading = false
        newState.response = nil
        newState.errorMessage = message
        newState.route = [.response]

    case .dismissedResponse:
        newState.route = []
    }
    return newState
}
