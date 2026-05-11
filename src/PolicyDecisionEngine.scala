import ujson.*

final case class PolicyDecisionEngine(scenarios: List[ScenarioSignal]):
  def summaryJson: Value =
    val critical = scenarios.count(_.riskBand == "critical")
    val watch = scenarios.count(_.riskBand == "watch")
    val activeFreeze = scenarios.count(_.changeFreezeActive)
    Obj(
      "summary" -> Obj(
        "tracked_scenarios" -> scenarios.size,
        "critical_scenarios" -> critical,
        "watch_scenarios" -> watch,
        "freeze_constrained_scenarios" -> activeFreeze,
        "avg_rollback_confidence" -> (scenarios.map(_.rollbackConfidence).sum / scenarios.size.toDouble)
      ),
      "scenarios" -> scenariosJson
    )

  def scenariosJson: Arr =
    Arr.from(scenarios.map(toJson))

  def scenarioJson(scenarioId: String): Option[Value] =
    scenarios.find(_.scenarioId == scenarioId).map(toJson)

  def analyzePayload(payload: Value): Value =
    val riskBand = payload.obj.get("risk_band").map(_.str).getOrElse("medium")
    val dependencyBreachCount = payload.obj.get("dependency_breach_count").flatMap(_.numOpt).map(_.toInt).getOrElse(0)
    val changeFreezeActive = payload.obj.get("change_freeze_active").flatMap(_.boolOpt).getOrElse(false)
    val rollbackConfidence = payload.obj.get("rollback_confidence").flatMap(_.numOpt).getOrElse(0.7)
    val customerExposurePct = payload.obj.get("customer_exposure_pct").flatMap(_.numOpt).map(_.toInt).getOrElse(10)

    var score = 20
    if riskBand == "critical" then score += 30
    else if riskBand == "high" then score += 20
    else if riskBand == "watch" then score += 10

    score += dependencyBreachCount * 9
    if changeFreezeActive then score += 18
    if rollbackConfidence < 0.5 then score += 16
    else if rollbackConfidence < 0.7 then score += 8
    if customerExposurePct >= 30 then score += 16
    else if customerExposurePct >= 15 then score += 8

    val (decision, action) =
      if score >= 74 then
        ("hold", "Delay release, isolate the failing dependency lane, and re-run the rollback drill before approving the change window.")
      else if score >= 46 then
        ("watch", "Route into a higher-friction review lane and require dependency owners to close open readiness gaps.")
      else
        ("approve", "Proceed with the scenario as planned while logging the baseline assumptions.")

    Obj(
      "decision" -> decision,
      "score" -> score,
      "recommended_action" -> action
    )

  private def toJson(signal: ScenarioSignal): Value =
    Obj(
      "scenario_id" -> signal.scenarioId,
      "label" -> signal.label,
      "mode" -> signal.mode,
      "owner_lane" -> signal.ownerLane,
      "dependency_breach_count" -> signal.dependencyBreachCount,
      "change_freeze_active" -> signal.changeFreezeActive,
      "rollback_confidence" -> signal.rollbackConfidence,
      "customer_exposure_pct" -> signal.customerExposurePct,
      "risk_band" -> signal.riskBand,
      "narrative" -> signal.narrative
    )

