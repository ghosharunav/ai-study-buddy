const COLORS = {
  beginner: 'bg-green-100 text-green-700',
  intermediate: 'bg-amber-100 text-amber-700',
  advanced: 'bg-red-100 text-red-700',
  eli5: 'bg-purple-100 text-purple-700',
}

export default function DifficultyBadge({ level }) {
  const cls = COLORS[level] || 'bg-slate-100 text-slate-700'
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${cls}`}>
      {level}
    </span>
  )
}
