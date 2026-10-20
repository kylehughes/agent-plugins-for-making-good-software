func receiptLines(for names: [String]) -> [String] {
    var result: [String] = []
    for name in names {
        if name.isEmpty {
            continue
        } else {
            result.append("Item: " + name)
        }
    }
    return result
}
