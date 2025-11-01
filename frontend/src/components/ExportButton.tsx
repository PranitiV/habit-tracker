import { useAuth } from "../hooks/useAuth"
import "../styling/ExportButton.css"

interface ExportButtonProps {
  habitId?: number
}

export default function ExportButton({ habitId }: ExportButtonProps) {
  const { token } = useAuth()
  const API_URL = (import.meta as any).env.VITE_API_URL || "http://localhost:8000"

  const handleExport = async (format: "csv" | "pdf") => {
    try {
      const url = habitId ? `${API_URL}/api/export/${format}?habit_id=${habitId}` : `${API_URL}/api/export/${format}`

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Export failed")
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = downloadUrl
      a.download = `habit_report.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(downloadUrl)
      document.body.removeChild(a)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="export-container">
      <button
        onClick={() => handleExport("csv")}
        className="export-button export-button-csv"
      >
        Export CSV
      </button>
      <button
        onClick={() => handleExport("pdf")}
        className="export-button export-button-pdf"
      >
        Export PDF
      </button>
    </div>
  )
}
