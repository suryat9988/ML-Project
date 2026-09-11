import { Link, NavLink } from "react-router-dom";

function PulseMark() {
  return (
    <svg className="pulse-mark" viewBox="0 0 64 24" aria-hidden="true">
      <path
        d="M1 14h12l4-10 5 20 5-14 3 6h34"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function AppHeader() {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link to="/" className="brand">
          <PulseMark />
          PulseLine
        </Link>
        <p className="tagline">Walk-in clinic queue. Human staff, digital tokens.</p>
        <nav className="nav">
          <NavLink to="/check-in" className="nav-link">
            Check in
          </NavLink>
          <NavLink to="/staff" className="nav-link">
            Staff
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
