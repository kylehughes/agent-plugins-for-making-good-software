struct TrustedText<State> {
    let value: String
}

enum Untrusted {}
enum HTMLTextEscaped {}

func renderHTML(_ text: TrustedText<HTMLTextEscaped>) {}

func demonstrateWrongTrustContext(_ raw: TrustedText<Untrusted>) {
    // expected-error: cannot convert value of type
    renderHTML(raw)
}
