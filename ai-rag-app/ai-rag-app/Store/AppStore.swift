//
//  AppStore.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Combine
import Foundation
import Observation

@Observable
final class AppStore {
    private(set) var state = AppState()

    private let queue = DispatchQueue(label: "net.apperdashery.demo.ai-rag-app")
    private let oshaClient: OshaAPIClientProtocol

    init(oshaClient: OshaAPIClientProtocol = OshaAPIClient()) {
        self.oshaClient = oshaClient
    }

    func dispatch(_ action: AppAction) {
        let currentState = state
        queue.async { [weak self] in
            guard let self else { return }
            let newState = appReducer(currentState, action)
            Task { @MainActor in
                self.state = newState
                self.runEffect(for: action)
            }
        }
    }

    private func runEffect(for action: AppAction) {
        guard case .osha(.askExpertTapped(let query)) = action else { return }
        Task {
            do {
                let response = try await oshaClient.askOshaPPE(query: query)
                dispatch(.osha(.responseReceived(response)))
            } catch let error as OshaAPIError {
                dispatch(.osha(.requestFailed(error.userMessage)))
            } catch {
                dispatch(.osha(.requestFailed(error.localizedDescription)))
            }
        }
    }
}
