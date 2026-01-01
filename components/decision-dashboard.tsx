"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, Send, CheckCircle2, XCircle, TrendingUp, Target, Database, Lightbulb, Brain } from "lucide-react"

interface DecisionResult {
  experience_id: number
  query: string
  answer: string
  strategy: string
  reason: string
  confidence: number
  data_source: string
  timestamp: string
}

export function DecisionDashboard() {
  const [query, setQuery] = useState("")
  const [result, setResult] = useState<DecisionResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [feedbackGiven, setFeedbackGiven] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    setIsLoading(true)
    setResult(null)
    setFeedbackGiven(false)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        throw new Error("API request failed")
      }

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error("[v0] Error:", error)
      setResult({
        experience_id: -1,
        query,
        answer: "System error: Unable to process query. Please try again.",
        strategy: "Error",
        reason: "API request failed",
        confidence: 0,
        data_source: "Error",
        timestamp: new Date().toISOString(),
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleFeedback = async (isHelpful: boolean) => {
    if (!result || feedbackGiven || result.experience_id === -1) return

    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          experience_id: result.experience_id,
          feedback: isHelpful ? 1 : 0,
        }),
      })
      setFeedbackGiven(true)
    } catch (error) {
      console.error("[v0] Feedback error:", error)
    }
  }

  const getStrategyIcon = (strategy: string) => {
    switch (strategy) {
      case "Rule-Based":
        return Target
      case "Retrieval":
        return Database
      case "ML":
        return TrendingUp
      case "Transformer":
        return Lightbulb
      default:
        return Target
    }
  }

  const getStrategyColor = (strategy: string) => {
    switch (strategy) {
      case "Rule-Based":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20"
      case "Retrieval":
        return "bg-green-500/10 text-green-500 border-green-500/20"
      case "ML":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20"
      case "Transformer":
        return "bg-orange-500/10 text-orange-500 border-orange-500/20"
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20"
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Query Input Panel */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle className="text-lg">Query Input Panel</CardTitle>
          <CardDescription>Submit your query for meta-learning analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query here..."
              className="min-h-[120px] resize-none text-base"
              disabled={isLoading}
            />
            <Button type="submit" disabled={!query.trim() || isLoading} size="lg" className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing Query...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-5 w-5" />
                  Submit Query
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Strategy Selection Panel */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-lg">Strategy Selection & Decision Explanation</CardTitle>
              <CardDescription>Meta-controller decision analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Selected Strategy */}
              <div className="space-y-3">
                <div className="text-sm font-medium text-muted-foreground">Selected Learning Strategy</div>
                <div className="flex items-center gap-3">
                  {(() => {
                    const Icon = getStrategyIcon(result.strategy)
                    return (
                      <div
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${getStrategyColor(result.strategy)}`}
                      >
                        <Icon className="h-6 w-6" />
                        <span className="text-lg font-semibold">{result.strategy} Engine</span>
                      </div>
                    )
                  })()}
                </div>
              </div>

              {/* Decision Reason */}
              <div className="space-y-3">
                <div className="text-sm font-medium text-muted-foreground">Decision Rationale</div>
                <div className="p-4 rounded-lg bg-muted/50 border border-border">
                  <p className="text-foreground">{result.reason}</p>
                </div>
              </div>

              {/* Confidence Indicator */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-muted-foreground">Confidence Score</div>
                  <Badge variant="outline" className="text-base font-semibold">
                    {result.confidence}%
                  </Badge>
                </div>
                <Progress value={result.confidence} className="h-3" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Low</span>
                  <span>High</span>
                </div>
              </div>

              {/* Data Source */}
              <div className="space-y-3">
                <div className="text-sm font-medium text-muted-foreground">Data Source</div>
                <Badge variant="secondary" className="text-sm">
                  <Database className="mr-2 h-3 w-3" />
                  {result.data_source}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Answer Panel */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-lg">System Response</CardTitle>
              <CardDescription>Generated answer from selected strategy</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-6 rounded-lg bg-muted/30 border border-border">
                <p className="text-foreground text-base leading-relaxed">{result.answer}</p>
              </div>
            </CardContent>
          </Card>

          {/* Feedback Evaluation */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-lg">System Evaluation</CardTitle>
              <CardDescription>Rate the quality of this response</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <Button
                  onClick={() => handleFeedback(true)}
                  disabled={feedbackGiven || result.experience_id === -1}
                  variant="outline"
                  size="lg"
                  className="flex-1 h-auto py-4"
                >
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  Helpful Response
                </Button>
                <Button
                  onClick={() => handleFeedback(false)}
                  disabled={feedbackGiven || result.experience_id === -1}
                  variant="outline"
                  size="lg"
                  className="flex-1 h-auto py-4"
                >
                  <XCircle className="mr-2 h-5 w-5" />
                  Not Helpful
                </Button>
              </div>
              {feedbackGiven && (
                <div className="mt-4 p-3 rounded-lg bg-primary/10 border border-primary/20 text-sm text-center">
                  Feedback recorded. Meta-controller updated with new learning data.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!result && !isLoading && (
        <Card className="border-2 border-dashed">
          <CardContent className="py-12">
            <div className="text-center space-y-4">
              <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-muted">
                <Brain className="h-10 w-10 text-muted-foreground" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-foreground">Ready for Analysis</h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                  Submit a query above to see the meta-learning system select and apply the optimal learning strategy.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      {/* System Maintenance / Admin Panel */}
      <Card className="border-2 border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Target className="h-5 w-5" />
            System Maintenance (Meta-Learning Ops)
          </CardTitle>
          <CardDescription>
            Trigger model updates based on collected experience data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={async () => {
              try {
                const res = await fetch("/api/retrain", { method: "POST" });
                const data = await res.json();
                alert(data.message || "Retraining started");
              } catch (e) {
                alert("Failed to trigger retraining");
              }
            }}
            variant="secondary"
            className="w-full sm:w-auto"
          >
            <TrendingUp className="mr-2 h-4 w-4" />
            Retrain ML Models (Use Feedback Data)
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
