import { type NextRequest, NextResponse } from "next/server"

// Main API handler acting as a proxy to the Python Backend
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query } = body

    if (!query || typeof query !== "string") {
      return NextResponse.json({ error: "Invalid query" }, { status: 400 })
    }

    console.log(`[Proxy] Forwarding query to Python backend: ${query}`)

    // Forward request to FastAPI backend
    try {
      const response = await fetch("http://localhost:8000/respond", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[Proxy] Backend error (${response.status}): ${errorText}`)
        throw new Error(`Python backend error: ${response.statusText}`)
      }

      const data = await response.json()
      console.log("[Proxy] Received response from backend:", data)

      // Map Python backend response to Frontend expected format
      return NextResponse.json({
        query: data.query,
        answer: data.answer,
        strategy: data.strategy,
        reason: data.reason,
        confidence: data.confidence * 100, // Frontend expects percentage 0-100? No, let's check. 
        // Wait, the simulation used 0.88, UI multiplies by 100 or displays as is?
        // UI: <Progress value={result.confidence} /> -> Progress usually takes 0-100.
        // UI: {result.confidence}% text. 
        // In the simulation code: `confidence: 0.88` but UI Badge says `{result.confidence}%`. 
        // If simulation sent 0.88, UI would show "0.88%".
        // Let's re-read the UI code.
        // UI: <Badge...>{result.confidence}%</Badge>
        // Simulation code: return confidence 0.88.
        // Wait, did the simulation send 88 or 0.88?
        // Simulation: confidence = 0.88 + ...; answer: `(Confidence: ${(confidence * 100).toFixed(0)}%)`
        // But the returned object has `confidence: Math.min(confidence, 0.95)` which is < 1.
        // If the UI displays `{result.confidence}%`, then 0.95 would be "0.95%". That seems wrong.
        // Let's check the previous screenshots... 
        // Screenshot 3 shows "0.8%". 
        // So the frontend *is* displaying the raw value as percentage.
        // If the Python backend returns 0.95, the UI will show 0.95%.
        // We should normalize this. If the UI expects 0-100, we should multiply by 100.
        // BUT, looking at the UI screenshot again: "0.8%". This implies the value passed was 0.8.
        // If we want it to look good (e.g. 80%), we should probably send 80.
        // Let's check `components/decision-dashboard.tsx` again.
        // `Progress value={result.confidence}`. Radix UI Progress value is usually 0-100.
        // So if we send 0.8, the progress bar is tiny (0.8%).
        // To fix the UI experience too, I will map the 0-1 float from Python to 0-100 int for Frontend.

        data_source: data.strategy + " Engine", // Map strategy to data source
        experience_id: data.experience_id,
        timestamp: data.timestamp,
      })

    } catch (fetchError) {
      console.error("[Proxy] Failed to connect to Python backend:", fetchError)
      return NextResponse.json({
        error: "Failed to connect to AI Engine. Is the Python server running on port 8000?"
      }, { status: 503 })
    }

  } catch (error) {
    console.error("[Proxy] API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
