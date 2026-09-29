export default function Loading({ label = 'Loading...' }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-500 py-6 justify-center">
      <span className="h-4 w-4 rounded-full border-2 border-slate-300 border-t-brand-500 animate-spin" />
      {label}
    </div>
  )
}
