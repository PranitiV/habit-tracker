import { useState, useEffect } from "react"
import { useAuth } from "../hooks/useAuth"
import HabitDetailModal from "./HabitDetailModal"
import ConfirmationModal from "./ConfirmationModal"
import "../styling/HabitCard.css"

interface Habit {
  id: number
  name: string
  htype: string
  goal: number | null
  archived: boolean
  created_at: string
  start_date: string
}

interface HabitCardProps {
  habit: Habit
  onDeleted: (habitId: number) => void
  onModalOpen: () => void
  onModalClose: () => void
}

export default function HabitCard({ habit, onDeleted, onModalOpen, onModalClose }: HabitCardProps) {
  const [loading, setLoading] = useState(false)
  const [todayLog, setTodayLog] = useState<any>(null)
  const [showModal, setShowModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [streak, setStreak] = useState(0)
  const { token } = useAuth()

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  useEffect(() => {
    fetchTodayLog()
    fetchStreak()
  }, [])

  const fetchTodayLog = async () => {
    try {
      const today = new Date().toISOString().split("T")[0]
      const response = await fetch(`${API_URL}/api/habits/${habit.id}/logs?start_date=${today}&end_date=${today}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setTodayLog(data[0] || null)
      }
    } catch (err) {
      console.error('fetchTodayLog error:', err)
    }
  }

  const fetchStreak = async () => {
    try {
      const today = new Date().toISOString().split("T")[0]
      const response = await fetch(`${API_URL}/api/habits/${habit.id}/insights?today=${today}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setStreak(data.seven_day_streak)
      }
    } catch (err) {
      console.error('Streak fetch error:', err)
    }
  }

  const handleLogToday = async (value?: number) => {
    setLoading(true)
    try {
      const today = new Date().toISOString().split("T")[0]
      const logData = {
        date: today,
        completed: habit.htype === "boolean" ? true : (value || 0) >= (habit.goal || 0),
        value: value || null,
      }
      
      const response = await fetch(`${API_URL}/api/habits/${habit.id}/logs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(logData),
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to log habit: ${response.status} ${errorText}`)
      }
      
      await fetchTodayLog()
      await fetchStreak()
    } catch (err) {
      console.error('Logging error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      const response = await fetch(`${API_URL}/api/habits/${habit.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to delete habit")
      }
      onDeleted(habit.id)
    } catch (err) {
      console.error(err)
    }
  }

  const isCompletedToday = todayLog?.completed
  
  const today = new Date().toISOString().split("T")[0]
  const startDate = habit.start_date
  const isBeforeStartDate = today < startDate
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
  }

  return (
    <>
      <div className="habit-card">
        <div className="habit-header">
          <div className="habit-info">
            <h3 className="habit-title">{habit.name}</h3>
            <div className="habit-meta">
              <p className="habit-type">
                {habit.htype === "boolean" ? "Yes/No" : habit.htype === "quantity" ? "Quantity" : "Time"}
                {habit.goal && ` • Goal: ${habit.goal}`}
              </p>
              {streak > 0 && <span className="streak-badge">🔥 {streak} day streak</span>}
            </div>
          </div>
          <button onClick={() => setShowDeleteModal(true)} className="delete-button">
            ✕
          </button>
        </div>

        <div className="habit-actions">
          {isBeforeStartDate ? (
            <div className="start-date-message">
              Start date is: {formatDate(startDate)}
            </div>
          ) : (
            <>
              {habit.htype === "boolean" ? (
                <button
                  onClick={() => handleLogToday()}
                  disabled={loading || isCompletedToday}
                  className={`log-button ${isCompletedToday ? "log-button-completed" : "log-button-pending"}`}
                >
                  {loading ? "Logging..." : isCompletedToday ? "✓ Done Today" : "Log Today"}
                </button>
              ) : (
                <>
                  <button
                    onClick={() => {
                      setShowModal(true)
                      onModalOpen()
                    }}
                    className="log-button-value"
                  >
                    {isCompletedToday ? `Logged: ${todayLog.value}` : "Log Value"}
                  </button>
                </>
              )}
              <button
                onClick={() => {
                  setShowModal(true)
                  onModalOpen()
                }}
                className="details-button"
              >
                Details
              </button>
            </>
          )}
        </div>
      </div>

      {showModal && (
        <HabitDetailModal
          habit={habit}
          onClose={() => {
            setShowModal(false)
            onModalClose()
            fetchTodayLog()
            fetchStreak()
          }}
        />
      )}

      <ConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title="Delete Habit"
        message={`Are you sure you want to delete "${habit.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonColor="bg-red-600 hover:bg-red-700"
      />
    </>
  )
}
