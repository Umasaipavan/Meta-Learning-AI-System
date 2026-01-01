"use client"
import { DecisionDashboard } from "@/components/decision-dashboard"
import { Brain, Network, Cpu } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent">
                <Brain className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-balance text-foreground">Meta-Learning AI System</h1>
                <p className="text-sm text-muted-foreground">Decision-Oriented Strategy Selection Console</p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Network className="h-4 w-4" />
                <span>4 Strategies</span>
              </div>
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                <span>Meta-Controller</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <DecisionDashboard />
      </div>
    </div>
  )
}
