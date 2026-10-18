# Fixture checks

Compile and run the focused checks without writing build products into this workspace:

```sh
scratch_dir=$(mktemp -d) || exit 1
trap 'rm -rf -- "$scratch_dir"' EXIT
swiftc -swift-version 6 -module-cache-path "$scratch_dir/module-cache" \
  Sources/Quantity.swift Tests/main.swift -o "$scratch_dir/quantity-tests" &&
  "$scratch_dir/quantity-tests"
```
