//
//  OshaRequestView.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import SwiftUI

struct OshaRequestView: View {
    @Environment(AppStore.self) var store
    @State private var query: String = ""

    private var trimmedQuery: String {
        query.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var body: some View {
        Form {
            Section("Ask about OSHA PPE regulations") {
                TextEditor(text: $query)
                    .frame(minHeight: 120)
            }

            Section {
                Button("Ask The Expert") {
                    store.dispatch(.osha(.askExpertTapped(query: trimmedQuery)))
                }
                .disabled(trimmedQuery.isEmpty || store.state.osha.isLoading)
            }
        }
        .navigationTitle("OSHA PPE Assistant")
        .overlay {
            if store.state.osha.isLoading {
                ProgressView("Asking the expert…")
                    .padding()
                    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }
}

#Preview {
    NavigationStack {
        OshaRequestView()
    }
    .environment(AppStore())
}
