//> using scala 3.7.4
//> using dep org.scalameta::munit:1.2.1
//> using dep com.lihaoyi::ujson:4.3.2

class PolicyDecisionSimulatorTest extends munit.FunSuite:
  private val engine = PolicyDecisionEngine(SampleScenarioData.scenarios)

  test("summary tracks the seeded scenarios") {
    val summary = engine.summaryJson("summary")
    assertEquals(summary("tracked_scenarios").num.toInt, 3)
    assertEquals(summary("critical_scenarios").num.toInt, 1)
  }

  test("critical payload holds the scenario") {
    val result = engine.analyzePayload(
      ujson.Obj(
        "risk_band" -> "critical",
        "dependency_breach_count" -> 3,
        "change_freeze_active" -> true,
        "rollback_confidence" -> 0.38,
        "customer_exposure_pct" -> 37
      )
    )

    assertEquals(result("decision").str, "hold")
    assert(result("score").num >= 74)
  }

