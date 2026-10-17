func demonstrateUseAfterConsume() {
    let value = OneShotValue(identifier: 1)
    _ = useOnce(value)
    _ = useOnce(value)
}
