import { useEffect, useState } from 'react';
import { navItems, resourcesMenu, useCaseMenu, type NavKey } from '../data/nav';

export function Header() {
  const [open, setOpen] = useState<NavKey | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(null);
        setMobileOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const toggle = (key: NavKey) => {
    if (key === 'useCases' || key === 'resources') {
      setOpen((current) => (current === key ? null : key));
      return;
    }
    setOpen(null);
  };

  return (
    <>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Google Antigravity unofficial home">
          <span className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span>Google Antigravity</span>
        </a>

        <nav className="desktop-nav" aria-label="Primary">
          {navItems.map((item) => (
            <a
              key={item.key}
              className={`nav-link ${open === item.key ? 'is-active' : ''}`}
              href={item.href}
              aria-expanded={item.dropdown ? open === item.key : undefined}
              onClick={(event) => {
                if (item.dropdown) event.preventDefault();
                toggle(item.key);
              }}
            >
              {item.label}
              {item.dropdown ? <span className="nav-caret">⌄</span> : null}
            </a>
          ))}
        </nav>

        <div className="header-actions">
          <a className="download-pill interactive" href="#download">
            Download <span aria-hidden="true">↓</span>
          </a>
          <button
            className="mobile-menu-button"
            type="button"
            aria-label="Open menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((value) => !value)}
          >
            <span />
            <span />
          </button>
        </div>
      </header>

      {open === 'useCases' ? (
        <DropdownPanel
          title="Built for developers in the agent-first era"
          body="Explore how Google Antigravity helps you build"
          cta="See overview"
          items={useCaseMenu}
          onClose={() => setOpen(null)}
        />
      ) : null}

      {open === 'resources' ? (
        <DropdownPanel
          title="Everything you need to stay up-to-date and get help"
          body=""
          items={resourcesMenu}
          onClose={() => setOpen(null)}
        />
      ) : null}

      {mobileOpen ? (
        <div className="mobile-panel">
          {navItems.map((item) => (
            <a key={item.key} href={item.href} onClick={() => setMobileOpen(false)}>
              {item.label}
            </a>
          ))}
          <a href="#download" onClick={() => setMobileOpen(false)}>
            Download
          </a>
        </div>
      ) : null}
    </>
  );
}

type DropdownItem = {
  label: string;
  href: string;
  icon?: string;
};

function DropdownPanel({
  title,
  body,
  cta,
  items,
  onClose,
}: {
  title: string;
  body: string;
  cta?: string;
  items: DropdownItem[];
  onClose: () => void;
}) {
  return (
    <div className="dropdown-scrim" onClick={onClose}>
      <section className="nav-dropdown" onClick={(event) => event.stopPropagation()}>
        <div className="dropdown-copy">
          <h2>{title}</h2>
          {body ? <p>{body}</p> : <p aria-hidden="true">&nbsp;</p>}
          {cta ? (
            <a className="soft-pill" href="#use-cases" onClick={onClose}>
              {cta}
            </a>
          ) : null}
        </div>
        <div className="dropdown-menu" role="menu">
          {items.map((item) => (
            <a key={item.label} href={item.href} role="menuitem" onClick={onClose}>
              <span className="menu-icon" aria-hidden="true">
                {item.icon ?? ''}
              </span>
              <span>{item.label}</span>
              <span aria-hidden="true">›</span>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
