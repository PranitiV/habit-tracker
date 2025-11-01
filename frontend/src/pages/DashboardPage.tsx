import { useState } from "react"
import { useAuth } from "../hooks/useAuth"
import HabitList from "../components/HabitList"
import AddHabitForm from "../components/AddHabitForm"
import ExportButton from "../components/ExportButton"
import "../styling/DashboardPage.css"

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleHabitAdded = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleModalOpen = () => {
    setIsModalOpen(true)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
  }

  return (
    <div className={`dashboard-container ${isModalOpen ? 'modal-open' : ''}`}>
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-info">
            <h1 className="header-title">Habit Tracker</h1>
            <p className="header-subtitle">{user?.email}</p>
          </div>
          <div className="header-actions">
            <ExportButton />
            <button
              onClick={logout}
              className="logout-button"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-grid">
          <div className="form-section">
            <AddHabitForm onHabitAdded={handleHabitAdded} />
          </div>

          <div className="habits-section">
            <HabitList 
              key={refreshTrigger} 
              onModalOpen={handleModalOpen}
              onModalClose={handleModalClose}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
