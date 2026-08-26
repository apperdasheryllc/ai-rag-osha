//
//  ai_rag_appApp.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import SwiftUI

@main
struct ai_rag_appApp: App {
    @State private var store = AppStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(store)
        }
    }
}
