enum ProbeError: Error { case failed }
func discardsTask() {
  Task { () throws(ProbeError) in throw .failed }
}
