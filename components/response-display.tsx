import { Card } from "@/components/ui/card"
import { CheckCircle2, Database } from "lucide-react"

interface ResponseDisplayProps {
  answer: string
  dataSource?: string
}

export function ResponseDisplay({ answer, dataSource }: ResponseDisplayProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <CheckCircle2 className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-foreground">AI Answer</p>
            {dataSource && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Database className="h-3 w-3" />
                <span>{dataSource}</span>
              </div>
            )}
          </div>
          <p className="text-foreground leading-relaxed">{answer}</p>
        </div>
      </div>
    </Card>
  )
}
