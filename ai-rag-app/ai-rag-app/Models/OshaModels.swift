//
//  OshaModels.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Foundation

struct OshaStandardQuery: Codable {
    let query: String
    let results: Int
}

struct OshaStandardResponse: Codable, Equatable {
    let answer: String
    let sources: [OshaSource]
}

struct OshaSource: Codable, Equatable, Identifiable {
    let citation: String
    let label: String
    let sourceUrl: String
    let text: String

    var id: String { citation + label }

    enum CodingKeys: String, CodingKey {
        case citation
        case label
        case sourceUrl = "source_url"
        case text
    }
}

struct OshaValidationError: Codable {
    let detail: String
}
