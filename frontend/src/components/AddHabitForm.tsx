import type React from "react"

import { useState } from "react"
import { useAuth } from "../hooks/useAuth"
import "../styling/AddHabitForm.css"

interface AddHabitFormProps {
  onHabitAdded: () => void
}

export default function AddHabitForm({ onHabitAdded }: AddHabitFormProps) {
  const [name, setName] = useState("")
  const [type, setType] = useState("boolean")
  const [goal, setGoal] = useState("")
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const { token } = useAuth()

  const API_URL = (import.meta as any).env.VITE_API_URL || "http://localhost:8000"

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/habits`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name,
          htype: type,
          goal: goal ? Number.parseInt(goal) : null,
          start_date: startDate,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to create habit")
      }

      setName("")
      setType("boolean")
      setGoal("")
      setStartDate(new Date().toISOString().split("T")[0])
      onHabitAdded()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create habit")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="add-habit-container">
      <h2 className="add-habit-title">Add New Habit</h2>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label className="form-label">Habit Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="form-input"
            placeholder="e.g., Morning Exercise"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="form-select"
          >
            <option value="boolean">Yes/No</option>
            <option value="quantity">Quantity</option>
            <option value="time">Time (minutes)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="form-input"
            required
          />
        </div>

        {type !== "boolean" && (
          <div className="form-group">
            <label className="form-label">Daily Goal</label>
            <input
              type="number"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="form-input"
              placeholder="e.g., 30"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="submit-button"
        >
          {loading ? "Adding..." : "Add Habit"}
        </button>
      </form>
    </div>
  )
}
