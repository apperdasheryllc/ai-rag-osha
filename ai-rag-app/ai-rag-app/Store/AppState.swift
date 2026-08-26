//
//  AppState.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Foundation

struct AppState: Equatable {
    var osha = OshaState()
}

struct OshaState: Equatable {
    var isLoading: Bool = false
    var response: OshaStandardResponse? = nil
    var errorMessage: String? = nil
    var route: [OshaRoute] = []
}

enum OshaRoute: Hashable {
    case response
}
