import { CheckCircle2, AlertTriangle, Info } from 'lucide-react'

/**
 * Encart de lecture coloré par tonalité (good / warn / info), utilisé par les
 * blocs « ce que ça veut dire » de la fiche territoire et des explorateurs.
 */
const TONE = {
  good: ['bg-emerald-50 border-emerald-200 text-emerald-900', CheckCircle2, 'text-emerald-600'],
  warn: ['bg-amber-50 border-amber-200 text-amber-900', AlertTriangle, 'text-amber-600'],
  info: ['bg-blue-50 border-blue-200 text-blue-900', Info, 'text-blue-600'],
}

export default function ToneCallout({ tone = 'info', children }) {
  const [cls, Icon, iconCls] = TONE[tone] || TONE.info
  return (
    <div className={`flex items-start gap-3 border rounded-xl p-4 ${cls}`}>
      <Icon className={`${iconCls} shrink-0 mt-0.5`} size={20} />
      <p className="text-sm leading-relaxed">{children}</p>
    </div>
  )
}
