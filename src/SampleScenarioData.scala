object SampleScenarioData:
  val scenarios: List[ScenarioSignal] = List(
    ScenarioSignal(
      "scn-901",
      "Pricing and entitlement cutover",
      "downside",
      "revenue-systems",
      dependencyBreachCount = 3,
      changeFreezeActive = true,
      rollbackConfidence = 0.36,
      customerExposurePct = 42,
      riskBand = "critical",
      narrative = "Revenue and identity changes are stacked into one cutover while rollback certainty is falling."
    ),
    ScenarioSignal(
      "scn-902",
      "Observability budget reset",
      "base",
      "platform-ops",
      dependencyBreachCount = 1,
      changeFreezeActive = false,
      rollbackConfidence = 0.68,
      customerExposurePct = 16,
      riskBand = "watch",
      narrative = "The plan is viable, but tail-latency and alert-noise dependencies still need cleanup before shipping."
    ),
    ScenarioSignal(
      "scn-903",
      "Self-serve launch expansion",
      "upside",
      "growth-platform",
      dependencyBreachCount = 0,
      changeFreezeActive = false,
      rollbackConfidence = 0.82,
      customerExposurePct = 9,
      riskBand = "stable",
      narrative = "Dependencies are clean and the rollout path is controlled enough to support expansion."
    )
  )

