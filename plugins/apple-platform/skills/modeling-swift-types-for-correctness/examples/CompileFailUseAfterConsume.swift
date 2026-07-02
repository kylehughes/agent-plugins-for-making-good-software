struct OneShotToken: ~Copyable {
    let identifier: Int
}

func consume(_ token: consuming OneShotToken) {
    _ = token.identifier
}

func demonstrateUseAfterConsume() {
    let token = OneShotToken(identifier: 1)
    consume(token)
    // expected-error: consumed more than once
    consume(token)
}
