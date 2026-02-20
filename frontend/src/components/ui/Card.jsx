/**
 * components/ui/Card.jsx — The standard "Linear" card component.
 *
 * Implements the card depth system from BRAND.md:
 *   - bg-white/5 lifts it above the #1a1f3a background
 *   - border-white/10 provides subtle edge definition
 *   - card-glow class adds the 1px cyan top-edge highlight + wash
 *   - Optional hover state for interactive cards
 *
 * Usage:
 *   <Card>...</Card>
 *   <Card hoverable onClick={...}>...</Card>
 *   <Card className="col-span-2">...</Card>
 */

export default function Card({ children, className = "", hoverable = false, onClick }) {
  return (
    <div
      onClick={onClick}
      className={[
        "card-glow bg-white/5 border border-white/10 rounded-lg",
        hoverable && "hover:border-cyan-400/30 hover:bg-white/[0.07] transition-all duration-200",
        onClick && "cursor-pointer",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </div>
  );
}

/** Card section with a header bar. */
export function CardHeader({ title, action }) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
      <h3 className="font-heading font-semibold text-sm uppercase tracking-wider text-slate-300">
        {title}
      </h3>
      {action && <div>{action}</div>}
    </div>
  );
}

/** Standard card body padding. */
export function CardBody({ children, className = "" }) {
  return <div className={`p-4 ${className}`}>{children}</div>;
}
