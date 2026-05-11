final case class ScenarioSignal(
    scenarioId: String,
    label: String,
    mode: String,
    ownerLane: String,
    dependencyBreachCount: Int,
    changeFreezeActive: Boolean,
    rollbackConfidence: Double,
    customerExposurePct: Int,
    riskBand: String,
    narrative: String
)

