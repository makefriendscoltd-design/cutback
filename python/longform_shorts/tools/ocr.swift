import Foundation
import Vision
import AppKit
for p in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: p), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("\(p)\t"); continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["ko-KR", "en-US"]
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg).perform([req])
    let t = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\u{1F}")
    print("\(p)\t\(t)")
}
