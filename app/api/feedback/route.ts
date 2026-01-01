import { type NextRequest, NextResponse } from "next/server"

// Correctly defined Feedback API - No imports from chat/route.ts
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { experience_id, feedback } = body

    if (typeof experience_id !== "number" || typeof feedback !== "number") {
      return NextResponse.json({ error: "Invalid parameters" }, { status: 400 })
    }

    console.log(`[Proxy] Forwarding feedback to Python backend: ID=${experience_id}, Feedback=${feedback}`)

    // Forward request to FastAPI backend
    try {
      const response = await fetch("http://localhost:8000/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          experience_id,
          feedback
        }),
      })

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[Proxy] Backend error (${response.status}): ${errorText}`)
        // Don't fail completely if backend feedback fails, just log it, 
        // or return the error. Let's return the error so UI knows.
        return NextResponse.json({ error: `Backend feedback failed: ${response.statusText}` }, { status: response.status })
      }

      const data = await response.json()
      console.log("[Proxy] Feedback response from backend:", data)

      return NextResponse.json(data)

    } catch (fetchError) {
      console.error("[Proxy] Failed to connect to Python backend:", fetchError)
      return NextResponse.json({
        error: "Failed to connect to AI Engine. Is the Python server running on port 8000?"
      }, { status: 503 })
    }

  } catch (error) {
    console.error("[Proxy] Feedback API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
