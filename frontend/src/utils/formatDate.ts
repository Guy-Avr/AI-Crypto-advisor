/**
 * Format ISO date string to readable date + time (e.g. "12 Feb 2025, 14:30").
 */
export function formatNewsDate(isoString: string): string {
  try {
    const d = new Date(isoString)
    if (Number.isNaN(d.getTime())) return isoString
    const date = d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
    const time = d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
    return `${date}, ${time}`
  } catch {
    return isoString
  }
}
