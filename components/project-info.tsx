import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Network, Layers, Database, Zap } from "lucide-react"

export function ProjectInfo() {
  return (
    <div className="space-y-6">
      {/* Overview */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Project Overview</h2>
        <p className="text-sm text-muted-foreground leading-relaxed mb-4">
          This system demonstrates meta-learning by intelligently selecting which learning strategy to use for each
          query, rather than relying on a single model.
        </p>
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary">AI/ML</Badge>
          <Badge variant="secondary">Meta-Learning</Badge>
          <Badge variant="secondary">Adaptive</Badge>
        </div>
      </Card>

      {/* Architecture */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">System Architecture</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <Network className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Input Analyzer</p>
              <p className="text-xs text-muted-foreground">Feature extraction</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent/10">
              <Zap className="h-4 w-4 text-accent" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Meta-Controller</p>
              <p className="text-xs text-muted-foreground">Strategy selection</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-chart-2/10">
              <Layers className="h-4 w-4 text-chart-2" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Base Learners</p>
              <p className="text-xs text-muted-foreground">4 learning strategies</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-chart-3/10">
              <Database className="h-4 w-4 text-chart-3" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Memory Store</p>
              <p className="text-xs text-muted-foreground">Feedback & learning</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Learning Strategies */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Learning Strategies</h2>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-1" />
            Rule-Based Engine
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-2" />
            Retrieval System
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-3" />
            Classical ML Models
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-4" />
            Transformer DL Model
          </li>
        </ul>
      </Card>
    </div>
  )
}
