import { NavLink } from "react-router-dom";

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    `rounded-full px-4 py-2 text-sm font-semibold transition ${
      isActive ? "bg-teal-300 text-slate-950" : "border border-white/10 text-slate-200 hover:bg-white/10"
    }`;

  return (
    <header className="border-b border-white/10 bg-slate-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-teal-300">Knowledge-Augmented Forecasting</p>
          <h1 className="text-2xl font-semibold text-sand">AlphaMind</h1>
        </div>
        <nav className="flex flex-wrap gap-3">
          <NavLink className={linkClass} to="/">
            Dashboard
          </NavLink>
          <NavLink className={linkClass} to="/guide">
            Guide
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
