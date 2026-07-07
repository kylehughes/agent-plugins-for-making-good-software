# Complete Shape Example

A full worked example applying every rule in this skill to a single file.

## Complete Shape Example

```swift
import UIKit

@MainActor
final class TypingDotsView: UIView {
    private let firstDotView = UIView()
    private let secondDotView = UIView()
    private let thirdDotView = UIView()

    override var intrinsicContentSize: CGSize {
        CGSize(width: .dotDiameter * CGFloat(.numberOfDots), height: .dotDiameter)
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        configureView()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        configureView()
    }

    private func configureView() {
        [firstDotView, secondDotView, thirdDotView].forEach(addSubview)
    }
}

extension TypingDotsView: CAAnimationDelegate {
    func animationDidStop(_ anim: CAAnimation, finished flag: Bool) {
        guard flag else { return }
        invalidateIntrinsicContentSize()
    }
}

extension TypingDotsView {
    enum AnimationPhase: CaseIterable, Sendable {
        case appearing
        case disappearing
        case idle
    }
}

extension CGFloat {
    fileprivate static let dotDiameter: CGFloat = 4
}

extension Int {
    fileprivate static let numberOfDots = 3
}

#if DEBUG
#Preview {
    TypingDotsView()
}
#endif
```
