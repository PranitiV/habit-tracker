import "../styling/ConfirmationModal.css"

interface ConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmButtonColor?: string
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmButtonColor = "confirmation-confirm-red"
}: ConfirmationModalProps) {
  if (!isOpen) return null

  const handleConfirm = () => {
    onConfirm()
    onClose()
  }

  return (
    <div className="confirmation-overlay">
      <div className="confirmation-container">
        <div className="confirmation-content">
          <h3 className="confirmation-title">{title}</h3>
          <p className="confirmation-message">{message}</p>
          
          <div className="confirmation-buttons">
            <button
              onClick={onClose}
              className="confirmation-button confirmation-cancel"
            >
              {cancelText}
            </button>
            <button
              onClick={handleConfirm}
              className={`confirmation-button confirmation-confirm ${confirmButtonColor}`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
