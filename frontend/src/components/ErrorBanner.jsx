export default function ErrorBanner({ message, onRetry }) {
  if (!message) return null
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm px-4 py-3 flex items-center justify-between gap-3">
      <span>{message}</span>
      {onRetry && (
        <button onClick={onRetry} className="text-red-700 underline underline-offset-2 shrink-0">
          Retry
        </button>
      )}
    </div>
  )
}
