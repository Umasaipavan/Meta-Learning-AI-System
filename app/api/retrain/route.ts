import { NextResponse } from "next/server"

export async function POST() {
    try {
        console.log("[Proxy] Forwarding retrain request to Python backend")

        const response = await fetch("http://localhost:8000/retrain", {
            method: "POST",
        })

        if (!response.ok) {
            const errorText = await response.text();
            return NextResponse.json({ error: `Backend retraining failed: ${response.statusText}`, details: errorText }, { status: response.status })
        }

        const data = await response.json()
        console.log("[Proxy] Retrain response from backend:", data)

        return NextResponse.json(data)

    } catch (error) {
        console.error("[Proxy] Retrain API error:", error)
        return NextResponse.json({ error: "Internal server error connecting to AI Engine" }, { status: 500 })
    }
}
