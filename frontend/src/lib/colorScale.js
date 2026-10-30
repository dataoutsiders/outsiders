/** Échelle de couleur séquentielle : gris clair (faible) -> émeraude (fort). */
export function greyToEmerald(t) {
  const x = Math.max(0, Math.min(1, t))
  const a = [203, 213, 225] // slate-300
  const b = [5, 150, 105] // emerald-600
  const c = a.map((v, i) => Math.round(v + (b[i] - v) * x))
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`
}

/** Renvoie une couleur de texte lisible (blanc/sombre) selon l'intensité de fond. */
export function textOn(t) {
  return t > 0.55 ? '#ffffff' : '#1f2937'
}
