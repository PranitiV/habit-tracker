import { useState, useEffect, useMemo } from "react"
import { useAuth } from "../hooks/useAuth"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import "../styling/HabitDetailModal.css"

interface Habit {
  id: number
  name: string
  htype: string
  goal: number | null
  archived: boolean
  created_at: string
  start_date: string
}

interface HabitDetailModalProps {
  habit: Habit
  onClose: () => void
}

export default function HabitDetailModal({ habit, onClose }: HabitDetailModalProps) {
  const [logs, setLogs] = useState<any[]>([])
  const [insights, setInsights] = useState<any>(null)
  const [weeklyTrend, setWeeklyTrend] = useState<any[]>([])
  const [monthlyTrend, setMonthlyTrend] = useState<any[]>([])
  const [chartData, setChartData] = useState<any[]>([])
  const [logValue, setLogValue] = useState("")
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0])
  const [activeTab, setActiveTab] = useState<"logs" | "weekly" | "monthly" | "daily">("logs")
  const { token } = useAuth()

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  useEffect(() => {
    fetchData()
  }, [])

  const chartSeriesData = useMemo(() => {
    const isBoolean = habit.htype === "boolean"
    return chartData.map((d) => ({
      ...d,
      y: isBoolean ? (d.completed ? 1 : 0) : (typeof d.value === "number" ? d.value : 0),
    }))
  }, [chartData, habit.htype])

  const fetchData = async () => {
    try {
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
      const today = new Date().toISOString().split("T")[0]

      const [logsRes, insightsRes, weeklyRes, monthlyRes, chartRes] = await Promise.all([
        fetch(`${API_URL}/api/habits/${habit.id}/logs?start_date=${thirtyDaysAgo}&end_date=${today}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/habits/${habit.id}/insights`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/habits/${habit.id}/trends/weekly`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/habits/${habit.id}/trends/monthly`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/habits/${habit.id}/chart-data?days=30`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ])

      if (logsRes.ok) setLogs(await logsRes.json())
      if (insightsRes.ok) setInsights(await insightsRes.json())
      if (weeklyRes.ok) setWeeklyTrend(await weeklyRes.json())
      if (monthlyRes.ok) setMonthlyTrend(await monthlyRes.json())
      if (chartRes.ok) setChartData(await chartRes.json())
    } catch (err) {
      console.error(err)
    }
  }

  const handleLogEntry = async () => {
    try {
      const response = await fetch(`${API_URL}/api/habits/${habit.id}/logs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          date: selectedDate,
          completed: habit.htype === "boolean" ? true : (Number.parseInt(logValue) || 0) >= (habit.goal || 0),
          value: habit.htype !== "boolean" ? Number.parseInt(logValue) || null : null,
        }),
      })

      if (response.ok) {
        setLogValue("")
        await fetchData()
      }
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">{habit.name}</h2>
          <button onClick={onClose} className="modal-close">
            ✕
          </button>
        </div>

        <div className="modal-content">
          {insights && (
            <div className="insights-grid">
              <div className="insight-card">
                <p className="insight-label">7-Day Streak</p>
                <p className="insight-value">{insights.seven_day_streak}</p>
              </div>
              <div className="insight-card">
                <p className="insight-label">28-Day Streak</p>
                <p className="insight-value">{insights.twenty_eight_day_streak}</p>
              </div>
              <div className="insight-card">
                <p className="insight-label">Overall Completion Rate</p>
                <p className="insight-value">{insights.avg_completion_percent.toFixed(1)}%</p>
              </div>
            </div>
          )}

          <div className="tabs-container">
            {["logs", "daily", "weekly", "monthly"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`tab-button ${activeTab === tab ? "tab-button-active" : ""}`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {activeTab === "logs" && (
            <div className="tab-content">
              <div className="log-form">
                <h3 className="log-form-title">Log Entry</h3>
                <div className="log-form-fields">
                  <div className="form-field">
                    <label className="form-label">Date</label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      min={habit.start_date}
                      className="form-input"
                    />
                  </div>

                  {habit.htype !== "boolean" && (
                    <div className="form-field">
                      <label className="form-label">
                        {habit.htype === "quantity" ? "Quantity" : "Time (minutes)"}
                      </label>
                      <input
                        type="number"
                        value={logValue}
                        onChange={(e) => setLogValue(e.target.value)}
                        className="form-input"
                        placeholder="Enter value"
                      />
                    </div>
                  )}

                  <button
                    onClick={handleLogEntry}
                    className="save-button"
                  >
                    Save Entry
                  </button>
                </div>
              </div>

              <div className="logs-section">
                <h3 className="logs-title">Recent Logs (Last 30 Days)</h3>
                <div className="logs-container">
                  {logs.length === 0 ? (
                    <p className="no-logs">No logs yet</p>
                  ) : (
                    logs.map((log) => (
                      <div key={log.id} className="log-item">
                        <span className="log-date">{log.date}</span>
                        <div className="log-details">
                          {log.completed && <span className="log-completed">✓</span>}
                          {log.value && <span className="log-value">{log.value}</span>}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "daily" && chartData.length > 0 && (
            <div className="chart-container">
              <h3 className="chart-title">Daily Completion (Last 30 Days)</h3>
                <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    tickFormatter={(v) => new Date(v).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                  />
                  {habit.htype === "boolean" ? (
                    <YAxis
                      stroke="#94a3b8"
                      domain={[0, 1]}
                      ticks={[0, 1]}
                      tickFormatter={(v) => (v === 1 ? "Yes" : "No")}
                    />
                  ) : (
                    <YAxis stroke="#94a3b8" />
                  )}
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Line type="monotone" dataKey="y" stroke="#10b981" dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {activeTab === "weekly" && weeklyTrend.length > 0 && (
            <div className="chart-container">
              <h3 className="chart-title">Weekly Completion Rate</h3>
              <ResponsiveContainer width="80%" height={200}>
                <BarChart data={weeklyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="week" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="completion_rate" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {activeTab === "monthly" && monthlyTrend.length > 0 && (
            <div className="chart-container">
              <h3 className="chart-title">Monthly Completion Rate</h3>
              <ResponsiveContainer width="80%" height={200}>
                <BarChart data={monthlyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="month" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="completion_rate" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}  
        </div>
      </div>
    </div>
  )
}
