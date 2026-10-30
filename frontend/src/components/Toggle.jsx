/**
 * Segmented control réutilisable.
 * @param {Array<[string, string]>} options  paires [valeur, libellé]
 */
export default function Toggle({ options, value, onChange, activeClass = 'bg-violet-600 text-white' }) {
  return (
    <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden text-sm">
      {options.map(([id, label]) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          className={`px-3 py-1.5 transition-colors ${
            value === id ? activeClass : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
