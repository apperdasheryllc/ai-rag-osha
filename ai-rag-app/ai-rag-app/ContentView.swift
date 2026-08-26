//
//  ContentView.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import SwiftUI

struct ContentView: View {
    @Environment(AppStore.self) var store

    var body: some View {
        NavigationStack(
            path: Binding(
                get: { store.state.osha.route },
                set: { newRoute in
                    if newRoute.isEmpty {
                        store.dispatch(.osha(.dismissedResponse))
                    }
                }
            )
        ) {
            OshaRequestView()
                .navigationDestination(for: OshaRoute.self) { _ in
                    OshaResponseView()
                }
        }
    }
}

#Preview {
    ContentView()
        .environment(AppStore())
}
