#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
composition_scratch=$(mktemp -d)
trap 'rm -rf -- "$composition_scratch"' EXIT
swiftc -swift-version 6 -module-cache-path "$composition_scratch/module-cache" \
  Sources/Quantity.swift Tests/main.swift -o "$composition_scratch/cart-checks"
# Compile checkpoint only: do not execute the binary.
