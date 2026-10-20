enum AcceptanceFailure: Error { case changedOutput }

@main
struct Acceptance {
    static func main() throws {
        let inputs = [[], [""], ["Tea", "Tea"], ["", " ", "Coffee", ""], ["☕", "A\nB"]]
        for names in inputs {
            let expected = names.filter { !$0.isEmpty }.map { "Item: " + $0 }
            guard receiptLines(for: names) == expected else {
                throw AcceptanceFailure.changedOutput
            }
        }
    }
}
