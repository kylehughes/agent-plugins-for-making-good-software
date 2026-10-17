struct TrustedText<State> {
    let value: String
}

enum Untrusted {}
enum HTMLTextEscaped {}

func renderHTML(_ text: TrustedText<HTMLTextEscaped>) {
    _ = text.value
}
