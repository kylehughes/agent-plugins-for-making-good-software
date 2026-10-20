precondition(receiptLines(for: []) == [])
precondition(receiptLines(for: ["", "Tea", "", "Coffee"]) == ["Item: Tea", "Item: Coffee"])
precondition(receiptLines(for: [" ", "Tea", "Tea"]) == ["Item:  ", "Item: Tea", "Item: Tea"])
