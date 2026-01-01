"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ThumbsUp, ThumbsDown, Check, Loader2 } from "lucide-react"

interface FeedbackButtonsProps {
  experienceId: number
}

export function FeedbackButtons({ experienceId }: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState<"helpful" | "not-helpful" | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFeedback = async (type: "helpful" | "not-helpful") => {
    if (experienceId === -1) return

    setIsSubmitting(true)

    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          experience_id: experienceId,
          feedback: type === "helpful" ? 1 : 0,
        }),
      })

      if (response.ok) {
        setFeedback(type)
        console.log("[v0] Feedback submitted successfully")
      } else {
        console.error("[v0] Feedback submission failed")
      }
    } catch (error) {
      console.error("[v0] Feedback error:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (feedback) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Check className="h-4 w-4 text-primary" />
        <span>Feedback recorded - System learning from your response</span>
      </div>
    )
  }

  if (experienceId === -1) {
    return null
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground">Was this helpful?</span>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback("helpful")}
        disabled={isSubmitting}
        className="gap-1"
      >
        {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ThumbsUp className="h-4 w-4" />}
        Helpful
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback("not-helpful")}
        disabled={isSubmitting}
        className="gap-1"
      >
        {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ThumbsDown className="h-4 w-4" />}
        Not Helpful
      </Button>
    </div>
  )
}
