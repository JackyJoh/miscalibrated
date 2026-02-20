/**
 * components/ui/Badge.jsx — Small status/label pills.
 *
 * Variants:
 *   cyan   — primary accent (platform labels, active states)
 *   amber  — secondary (warnings, secondary metrics)
 *   rose   — danger/negative (NO direction, losses)
 *   slate  — neutral/muted
 *   green  — positive (YES direction, gains)
 *
 * Usage:
 *   <Badge variant="cyan">Kalshi</Badge>
 *   <Badge variant="rose">NO</Badge>
 */

const VARIANT_CLASSES = {
  cyan:  "bg-cyan-400/10 text-cyan-400 border-cyan-400/20",
  amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  rose:  "bg-rose-400/10 text-rose-400 border-rose-400/20",
  slate: "bg-white/5 text-slate-400 border-white/10",
  green: "bg-emerald-400/10 text-emerald-400 border-emerald-400/20",
};

export default function Badge({ children, variant = "slate" }) {
  const classes = VARIANT_CLASSES[variant] ?? VARIANT_CLASSES.slate;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-heading font-semibold uppercase tracking-wider border ${classes}`}
    >
      {children}
    </span>
  );
}
