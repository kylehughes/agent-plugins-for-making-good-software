enum Draft {}
enum Validated {}

struct Form<State> {}

extension Form where State == Validated {
    func submit() {}
}

func demonstrateWrongTypestate(_ draft: Form<Draft>) {
    // expected-error: requires the types 'Draft' and 'Validated' be equivalent
    draft.submit()
}
