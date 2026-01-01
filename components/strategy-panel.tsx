import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Lightbulb, Target, Gauge } from "lucide-react"

interface StrategyPanelProps {
  strategy: string
  reason: string
  confidence: number
}

const strategyColors: Record<string, string> = {
  "Rule-Based": "bg-chart-1",
  Retrieval: "bg-chart-2",
  "Classical ML": "bg-chart-3",
  Transformer: "bg-chart-4",
}

export function StrategyPanel({ strategy, reason, confidence }: StrategyPanelProps) {
  const confidencePercent = Math.round(confidence * 100)

  return (
    <Card className="p-6 bg-card border-2 border-accent/20">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-accent" />
          <h3 className="text-sm font-semibold text-foreground">Strategy Explanation</h3>
        </div>

        <div className="space-y-4">
          {/* Selected Strategy */}
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Selected Strategy:</p>
            <Badge variant="secondary" className="text-sm font-medium">
              {strategy}
            </Badge>
          </div>

          {/* Reason */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs font-medium text-muted-foreground">Reason for Selection:</p>
            </div>
            <p className="text-sm text-foreground leading-relaxed">{reason}</p>
          </div>

          {/* Confidence Score */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Gauge className="h-4 w-4 text-muted-foreground" />
                <p className="text-xs font-medium text-muted-foreground">Confidence Score:</p>
              </div>
              <span className="text-sm font-semibold text-foreground">{confidencePercent}%</span>
            </div>
            <Progress value={confidencePercent} className="h-2" />
          </div>
        </div>
      </div>
    </Card>
  )
}
