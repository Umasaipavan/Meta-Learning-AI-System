"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card } from "@/components/ui/card"
import { ResponseDisplay } from "@/components/response-display"
import { StrategyPanel } from "@/components/strategy-panel"
import { FeedbackButtons } from "@/components/feedback-buttons"
import { Loader2, Send } from "lucide-react"

interface Message {
  id: string
  experience_id: number
  query: string
  answer: string
  strategy: string
  reason: string
  confidence: number
  data_source: string
  timestamp: Date
}

export function ChatInterface() {
  const [query, setQuery] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    setIsLoading(true)
    const userQuery = query
    setQuery("")

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userQuery }),
      })

      if (!response.ok) {
        throw new Error("API request failed")
      }

      const data = await response.json()

      const newMessage: Message = {
        id: Date.now().toString(),
        experience_id: data.experience_id,
        query: userQuery,
        answer: data.answer,
        strategy: data.strategy,
        reason: data.reason,
        confidence: data.confidence,
        data_source: data.data_source,
        timestamp: new Date(data.timestamp),
      }

      setMessages((prev) => [...prev, newMessage])
    } catch (error) {
      console.error("[v0] Error:", error)
      // Show error message to user
      const errorMessage: Message = {
        id: Date.now().toString(),
        experience_id: -1,
        query: userQuery,
        answer: "Sorry, there was an error processing your request. Please try again.",
        strategy: "Error",
        reason: "API request failed",
        confidence: 0,
        data_source: "Error",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Input Area */}
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="query" className="text-sm font-medium text-foreground">
              Ask a question
            </label>
            <Textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question..."
              className="min-h-[100px] resize-none"
              disabled={isLoading}
            />
          </div>
          <Button type="submit" disabled={!query.trim() || isLoading} className="w-full sm:w-auto">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Ask AI
              </>
            )}
          </Button>
        </form>
      </Card>

      {/* Messages */}
      <div className="space-y-6">
        {messages.map((message) => (
          <div key={message.id} className="space-y-4">
            {/* User Query */}
            <Card className="p-4 bg-muted/50">
              <p className="text-sm font-medium text-muted-foreground mb-1">You asked:</p>
              <p className="text-foreground">{message.query}</p>
            </Card>

            {/* AI Response */}
            <ResponseDisplay answer={message.answer} dataSource={message.data_source} />

            {/* Strategy Explanation */}
            <StrategyPanel strategy={message.strategy} reason={message.reason} confidence={message.confidence} />

            {/* Feedback */}
            <FeedbackButtons experienceId={message.experience_id} />
          </div>
        ))}
      </div>

      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <Card className="p-12 text-center">
          <div className="mx-auto max-w-md space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
              <Send className="h-8 w-8 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Start a conversation</h3>
              <p className="text-sm text-muted-foreground text-balance">
                Ask any question and watch the AI system intelligently select the best learning strategy to answer it.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
