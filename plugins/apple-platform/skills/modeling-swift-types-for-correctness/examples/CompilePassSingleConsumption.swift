func demonstrateSingleConsumption() {
    let value = OneShotValue(identifier: 1)
    _ = useOnce(value)
}
