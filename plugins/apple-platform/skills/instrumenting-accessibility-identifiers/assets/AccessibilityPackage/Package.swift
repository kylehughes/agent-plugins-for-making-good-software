// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "Accessibility",
    platforms: [
        .iOS(.v16),
    ],
    products: [
        .library(
            name: "AccessibilityUI",
            targets: ["AccessibilityUI"]
        ),
        .library(
            name: "AccessibilityUIForTest",
            targets: ["AccessibilityUIForTest"]
        ),
    ],
    targets: [
        .target(name: "AccessibilityUI"),
        .target(
            name: "AccessibilityUIForTest",
            dependencies: ["AccessibilityUI"]
        ),
        .testTarget(
            name: "AccessibilityUITests",
            dependencies: ["AccessibilityUI"]
        ),
    ],
    swiftLanguageModes: [.v6]
)
