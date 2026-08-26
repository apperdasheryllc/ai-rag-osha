//
//  AppAction.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Foundation

enum AppAction {
    case osha(OshaAction)
}

enum OshaAction {
    case askExpertTapped(query: String)
    case responseReceived(OshaStandardResponse)
    case requestFailed(String)
    case dismissedResponse
}
