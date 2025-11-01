import { useState, useEffect } from "react"
import { useAuth } from "../hooks/useAuth"
import HabitCard from "./HabitCard"
import "../styling/HabitList.css"

interface Habit {
  id: number
  name: string
  htype: string
  goal: number | null
  archived: boolean
  created_at: string
  start_date: string
}

interface HabitListProps {
  onModalOpen: () => void
  onModalClose: () => void
}

export default function HabitList({ onModalOpen, onModalClose }: HabitListProps) {
  const [habits, setHabits] = useState<Habit[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const { token } = useAuth()

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  useEffect(() => {
    fetchHabits()
  }, [])

  const fetchHabits = async () => {
    try {
      const response = await fetch(`${API_URL}/api/habits`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to fetch habits")
      }
      const data = await response.json()
      setHabits(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch habits")
    } finally {
      setLoading(false)
    }
  }

  const handleHabitDeleted = (habitId: number) => {
    setHabits(habits.filter((h) => h.id !== habitId))
  }

  if (loading) {
    return <div className="loading-message">Loading habits...</div>
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  if (habits.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-state-text">No habits yet. Create one to get started!</p>
      </div>
    )
  }

  return (
    <div className="habits-container">
      <h2 className="habits-title">Your Habits</h2>
      {habits.map((habit) => (
        <HabitCard 
          key={habit.id} 
          habit={habit} 
          onDeleted={handleHabitDeleted}
          onModalOpen={onModalOpen}
          onModalClose={onModalClose}
        />
      ))}
    </div>
  )
}
