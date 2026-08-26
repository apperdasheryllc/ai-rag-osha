//
//  OshaAPIClient.swift
//  ai-rag-app
//
//  Created by Graham Diehl on 8/26/26.
//

import Foundation

enum OshaAPIError: Error {
    case invalidResponse
    case server(statusCode: Int, message: String)
    case decoding(Error)
    case transport(Error)

    var userMessage: String {
        switch self {
        case .invalidResponse:
            return "Received an unexpected response from the server."
        case .server(_, let message):
            return message
        case .decoding:
            return "Couldn't read the server's response."
        case .transport(let error):
            return error.localizedDescription
        }
    }
}

protocol OshaAPIClientProtocol {
    func askOshaPPE(query: String) async throws -> OshaStandardResponse
}

final class OshaAPIClient: OshaAPIClientProtocol {
    private let baseURL: URL
    private let session: URLSession

    init(baseURL: URL = URL(string: "http://localhost:8000")!, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    func askOshaPPE(query: String) async throws -> OshaStandardResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/v1/osha/ppe"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(OshaStandardQuery(query: query, results: 5))

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw OshaAPIError.transport(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw OshaAPIError.invalidResponse
        }

        guard (200..<300).contains(httpResponse.statusCode) else {
            let message = (try? JSONDecoder().decode(OshaValidationError.self, from: data))?.detail
                ?? "Request failed with status \(httpResponse.statusCode)."
            throw OshaAPIError.server(statusCode: httpResponse.statusCode, message: message)
        }

        do {
            return try JSONDecoder().decode(OshaStandardResponse.self, from: data)
        } catch {
            throw OshaAPIError.decoding(error)
        }
    }
}
