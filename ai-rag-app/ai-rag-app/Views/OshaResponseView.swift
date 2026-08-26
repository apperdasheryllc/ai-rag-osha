//
//  OshaResponseView.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import SwiftUI

struct OshaResponseView: View {
    @Environment(AppStore.self) var store

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let errorMessage = store.state.osha.errorMessage {
                    errorContent(errorMessage)
                } else if let response = store.state.osha.response {
                    answerContent(response)
                } else {
                    Text("No response available.")
                        .foregroundStyle(.secondary)
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .navigationTitle("Expert Answer")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func errorContent(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Something went wrong", systemImage: "exclamationmark.triangle.fill")
                .font(.headline)
                .foregroundStyle(.red)
            Text(message)
                .foregroundStyle(.secondary)
            Button("Try Again") {
                store.dispatch(.osha(.dismissedResponse))
            }
        }
    }

    private func answerContent(_ response: OshaStandardResponse) -> some View {
        VStack(alignment: .leading, spacing: 20) {
            Text(response.answer)
                .font(.body)

            if !response.sources.isEmpty {
                Divider()

                Text("Sources")
                    .font(.headline)

                ForEach(response.sources) { source in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(source.label)
                            .font(.subheadline.bold())
                        Text(source.citation)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text(source.text)
                            .font(.footnote)
                        if let url = URL(string: source.sourceUrl) {
                            Link("View source", destination: url)
                                .font(.footnote)
                        }
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        OshaResponseView()
    }
    .environment(AppStore())
}
