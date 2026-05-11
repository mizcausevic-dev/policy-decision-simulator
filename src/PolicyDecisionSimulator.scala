//> using scala 3.7.4
//> using dep com.lihaoyi::ujson:4.3.2

import com.sun.net.httpserver.{HttpExchange, HttpServer}
import java.net.InetSocketAddress
import java.nio.charset.StandardCharsets
import scala.util.Using

object PolicyDecisionSimulator:
  private val DefaultPort = 4514

  def main(args: Array[String]): Unit =
    val port = sys.env.get("PORT").flatMap(_.toIntOption).getOrElse(DefaultPort)
    val server = HttpServer.create(InetSocketAddress("127.0.0.1", port), 0)
    val app = PolicyDecisionApp(PolicyDecisionEngine(SampleScenarioData.scenarios))

    server.createContext("/", exchange => app.route(exchange))
    server.setExecutor(null)

    try
      server.start()
      println(s"Policy Decision Simulator listening on http://127.0.0.1:$port")
      println(s"Docs available at http://127.0.0.1:$port/docs")
    catch
      case _: java.net.BindException =>
        Console.err.println(s"Policy Decision Simulator could not start because port $port is already in use.")
        Console.err.println("Set a different port before running again, for example:")
        Console.err.println("""$env:PORT = "4520"""")
        Console.err.println("scala-cli run src")
        sys.exit(1)

final case class PolicyDecisionApp(engine: PolicyDecisionEngine):
  def route(exchange: HttpExchange): Unit =
    val path = Option(exchange.getRequestURI).map(_.getPath).getOrElse("/")
    val method = exchange.getRequestMethod

    (method, path) match
      case ("GET", "/") =>
        json(exchange, 200, ujson.Obj("service" -> "policy-decision-simulator", "status" -> "ok", "docs" -> "/docs"))
      case ("GET", "/docs") =>
        html(exchange, docsPage)
      case ("GET", "/api/dashboard/summary") =>
        json(exchange, 200, engine.summaryJson)
      case ("GET", "/api/sample") =>
        json(exchange, 200, ujson.Obj("scenarios" -> engine.scenariosJson))
      case ("GET", p) if p.startsWith("/api/scenarios/") =>
        val scenarioId = p.stripPrefix("/api/scenarios/")
        engine.scenarioJson(scenarioId) match
          case Some(payload) => json(exchange, 200, payload)
          case None => json(exchange, 404, ujson.Obj("error" -> "Scenario not found"))
      case ("POST", "/api/analyze/scenario") =>
        val body = Using.resource(scala.io.Source.fromInputStream(exchange.getRequestBody))(src => src.mkString)
        val payload = ujson.read(if body.trim.nonEmpty then body else "{}")
        json(exchange, 200, engine.analyzePayload(payload))
      case _ =>
        json(exchange, 404, ujson.Obj("error" -> "Not found"))

  private def json(exchange: HttpExchange, status: Int, payload: ujson.Value): Unit =
    val bytes = ujson.write(payload, indent = 2).getBytes(StandardCharsets.UTF_8)
    exchange.getResponseHeaders.add("Content-Type", "application/json")
    exchange.sendResponseHeaders(status, bytes.length.toLong)
    Using.resource(exchange.getResponseBody)(_.write(bytes))

  private def html(exchange: HttpExchange, body: String): Unit =
    val bytes = body.getBytes(StandardCharsets.UTF_8)
    exchange.getResponseHeaders.add("Content-Type", "text/html; charset=utf-8")
    exchange.sendResponseHeaders(200, bytes.length.toLong)
    Using.resource(exchange.getResponseBody)(_.write(bytes))

  private val docsPage =
    """<!doctype html>
      |<html lang="en">
      |  <head>
      |    <meta charset="utf-8">
      |    <title>Policy Decision Simulator</title>
      |    <style>
      |      body { font-family: Segoe UI, Arial, sans-serif; margin: 40px; background: #091423; color: #e8edde; }
      |      code, pre { background: #12213a; color: #9dd0ff; padding: 4px 8px; border-radius: 8px; }
      |      pre { padding: 16px; overflow: auto; }
      |      .panel { background: #13233a; border: 1px solid #274465; border-radius: 18px; padding: 20px; margin-bottom: 20px; }
      |    </style>
      |  </head>
      |  <body>
      |    <h1>Policy Decision Simulator</h1>
      |    <div class="panel">
      |      <ul>
      |        <li><code>GET /</code></li>
      |        <li><code>GET /docs</code></li>
      |        <li><code>GET /api/dashboard/summary</code></li>
      |        <li><code>GET /api/sample</code></li>
      |        <li><code>GET /api/scenarios/{scenarioId}</code></li>
      |        <li><code>POST /api/analyze/scenario</code></li>
      |      </ul>
      |    </div>
      |    <div class="panel">
      |      <pre>{
      |  "risk_band": "high",
      |  "dependency_breach_count": 2,
      |  "change_freeze_active": true,
      |  "rollback_confidence": 0.41,
      |  "customer_exposure_pct": 37
      |}</pre>
      |    </div>
      |  </body>
      |</html>
      |""".stripMargin

