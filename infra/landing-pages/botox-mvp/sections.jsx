// ============== NAV ==============
const NAV_BLUE = "#5BB5D6";
const NAV_PINK = "#F4A6BB";

// Reusable pink CTA button — hover turns blue, with subtle lift
const PinkCTA = ({ href, children, target, rel, style = {}, size = "md" }) => {
  const [hover, setHover] = React.useState(false);
  const padding = size === "lg" ? "18px 34px" : size === "sm" ? "12px 22px" : "16px 30px";
  const fontSize = size === "lg" ? 12.5 : size === "sm" ? 11 : 12;
  return (
    <a
      href={href}
      target={target}
      rel={rel}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 10,
        padding,
        background: hover ? NAV_BLUE : NAV_PINK,
        color: "#FFFFFF",
        borderRadius: 999,
        fontFamily: "Montserrat, sans-serif", fontWeight: 600,
        fontSize, letterSpacing: "0.16em", textTransform: "uppercase",
        transform: hover ? "translateY(-1px)" : "translateY(0)",
        boxShadow: hover
          ? "0 12px 26px -10px rgba(91,181,214,0.55)"
          : "0 6px 16px -10px rgba(244,166,187,0.6)",
        transition: "all .28s cubic-bezier(.65,0,.35,1)",
        ...style,
      }}
    >
      {children}
    </a>
  );
};

const NavLink = ({ href, label, active }) => {
  const [hover, setHover] = React.useState(false);
  const color = active ? NAV_PINK : hover ? NAV_BLUE : "var(--ink)";
  return (
    <a
      href={href}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        position: "relative",
        fontFamily: "Montserrat, sans-serif",
        fontWeight: 600,
        fontSize: 12,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        color,
        padding: "8px 0",
        cursor: "pointer",
        transition: "color .25s ease",
      }}
    >
      {label}
      <span style={{
        position: "absolute", left: 0, right: 0, bottom: 2, height: 1.5,
        background: active ? NAV_PINK : NAV_BLUE,
        transformOrigin: "left center",
        transform: `scaleX(${active || hover ? 1 : 0})`,
        transition: "transform .35s cubic-bezier(.65,0,.35,1)",
      }} />
    </a>
  );
};

const Nav = ({ accent }) => {
  const [scrolled, setScrolled] = React.useState(false);
  const [active, setActive] = React.useState("inicio");
  const [waHover, setWaHover] = React.useState(false);
  const [menuOpen, setMenuOpen] = React.useState(false);

  React.useEffect(() => {
    const sections = [
      { id: "inicio",     y: 0 },
      { id: "beneficios", el: () => document.getElementById("beneficios") },
      { id: "resultados", el: () => document.getElementById("resultados") },
      { id: "proceso",    el: () => document.getElementById("proceso") },
      { id: "reservar",   el: () => document.getElementById("reservar") },
    ];
    const onScroll = () => {
      setScrolled(window.scrollY > 30);
      const y = window.scrollY + 140;
      let current = "inicio";
      for (const s of sections) {
        const top = s.el ? (s.el()?.offsetTop ?? Infinity) : s.y;
        if (y >= top) current = s.id;
      }
      setActive(current);
    };
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll when menu open
  React.useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  const links = [
    { id: "inicio",     href: "#",            label: "Inicio" },
    { id: "beneficios", href: "#beneficios",  label: "Nosotros" },
    { id: "resultados", href: "#resultados",  label: "Resultados" },
    { id: "proceso",    href: "#proceso",     label: "Tratamiento" },
    { id: "reservar",   href: "#reservar",    label: "Contacto" },
  ];

  return (
    <>
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 50,
        transition: "all .35s ease",
        background: "rgba(255,255,255,0.96)",
        backdropFilter: "blur(14px)",
        borderBottom: scrolled ? "1px solid var(--line)" : "1px solid transparent",
      }}>
        <div style={{
          maxWidth: 1240, margin: "0 auto",
          padding: scrolled ? "12px 20px" : "16px 20px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          transition: "padding .35s ease",
        }}>
          <Logo size={22} showTagline={true} />
          {/* Desktop nav */}
          <div className="nav-desktop" style={{ gap: 28, alignItems: "center" }}>
            {links.map(l => (
              <NavLink key={l.id} href={l.href} label={l.label} active={active === l.id} />
            ))}
            <a
              href="https://wa.me/51980727888"
              onMouseEnter={() => setWaHover(true)}
              onMouseLeave={() => setWaHover(false)}
              style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                padding: "12px 22px",
                background: waHover ? NAV_BLUE : NAV_PINK,
                color: "#FFFFFF",
                borderRadius: 999,
                fontFamily: "Montserrat, sans-serif", fontWeight: 600,
                fontSize: 11, letterSpacing: "0.14em", textTransform: "uppercase",
                transform: waHover ? "translateY(-1px)" : "translateY(0)",
                boxShadow: waHover
                  ? "0 10px 22px -10px rgba(91,181,214,0.55)"
                  : "0 6px 16px -10px rgba(244,166,187,0.6)",
                transition: "all .28s cubic-bezier(.65,0,.35,1)",
              }}
            >Reserva aquí</a>
          </div>
          {/* Mobile hamburger */}
          <button
            className="nav-mobile-toggle"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menú"
            style={{
              border: "none", background: "transparent", cursor: "pointer",
              width: 44, height: 44, alignItems: "center", justifyContent: "center",
              color: "var(--ink)",
            }}
          >
            {menuOpen ? (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
            ) : (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4 8h16M4 16h16"/></svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile menu drawer */}
      {menuOpen && (
        <div style={{
          position: "fixed", inset: 0, top: 60, zIndex: 49,
          background: "#FFFFFF",
          padding: "32px 24px",
          display: "flex", flexDirection: "column", gap: 4,
        }}>
          {links.map(l => (
            <a
              key={l.id}
              href={l.href}
              onClick={() => setMenuOpen(false)}
              style={{
                padding: "18px 8px",
                fontFamily: "Montserrat, sans-serif",
                fontWeight: 600,
                fontSize: 16,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: active === l.id ? NAV_PINK : "var(--ink)",
                borderBottom: "1px solid var(--line)",
              }}
            >{l.label}</a>
          ))}
          <a
            href="https://wa.me/51980727888"
            onClick={() => setMenuOpen(false)}
            style={{
              marginTop: 28,
              display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 10,
              padding: "16px 24px",
              background: NAV_PINK, color: "#FFFFFF",
              borderRadius: 999,
              fontFamily: "Montserrat, sans-serif", fontWeight: 600,
              fontSize: 12, letterSpacing: "0.16em", textTransform: "uppercase",
            }}
          >Reserva aquí</a>
        </div>
      )}
    </>
  );
};

// ============== HERO — matches livskin.site ==============
const Hero = ({ headline, sub, accent }) => {
  return (
    <section className="hero-section">
      <style>{`
        .hero-section {
          background: var(--bg);
          padding: calc(var(--sp-y) + 24px) var(--sp-x) calc(var(--sp-y) * 0.7);
        }
        @media (min-width: 1024px) {
          .hero-section { min-height: 92vh; display: flex; align-items: center; }
        }

        .hero-inner {
          max-width: 1240px;
          margin: 0 auto;
          width: 100%;
          display: grid;
          grid-template-columns: 1fr;
          gap: 28px;
          align-items: center;
        }
        @media (min-width: 720px) {
          .hero-inner { grid-template-columns: 1fr 1fr; gap: 40px; }
        }
        @media (min-width: 1024px) {
          .hero-inner { gap: 80px; }
        }
      `}</style>
      <div className="hero-inner">
        <div className="hero-text" style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div className="eyebrow" style={{ color: accent, marginBottom: 18, fontSize: 12, letterSpacing: "0.32em" }}>
            BIENVENIDO A LIVSKIN
          </div>
          <h1 className="display-bold" style={{
            fontSize: "clamp(34px, 6.5vw, 56px)", lineHeight: 1.08, fontWeight: 700,
            color: "var(--ink)", letterSpacing: "-0.005em", marginBottom: 18,
          }}>
            {headline.split("\n").map((l, i) => <div key={i}>{l}</div>)}
          </h1>
          <p style={{ fontSize: "clamp(15px, 2.2vw, 17px)", lineHeight: 1.6, color: "var(--ink-soft)", maxWidth: 460, marginBottom: 28 }}>{sub}</p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "center" }}>
            <PinkCTA href="https://wa.me/51980727888?text=Hola%20Livskin%2C%20quisiera%20agendar%20una%20valoraci%C3%B3n%20de%20Botox" size="md">
              <Icon name="wa" size={15} color="#FFFFFF" /> Reservar por WhatsApp
            </PinkCTA>
            <a href="#proceso" style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              padding: "14px 22px", background: "transparent",
              border: "1.5px solid var(--ink)", color: "var(--ink)",
              borderRadius: 999, fontFamily: "Montserrat, sans-serif", fontWeight: 600,
              fontSize: 11, letterSpacing: "0.14em", textTransform: "uppercase",
            }}>Conocer el proceso</a>
          </div>
        </div>
        <div style={{ position: "relative" }}>
          <Placeholder tone="pink" ratio="4/5" kind="portrait" />
        </div>
      </div>
    </section>
  );
};

// ============== BENEFICIOS — pale pink section like site ==============
const Benefits = ({ accent }) => {
  const items = [
    { icon: "leaf",    title: "Atención por Especialista", desc: "Cada tratamiento es evaluado y realizado con criterio especialista." },
    { icon: "heart",   title: "Resultados Naturales",      desc: "Buscamos equilibrio y armonía, no cambios artificiales." },
    { icon: "sparkle", title: "Personalización",           desc: "Analizamos tu rostro de forma integral, no solo una zona." },
  ];
  return (
    <section id="beneficios" className="sec" style={{ background: "var(--bg-pink)" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
        <div className="eyebrow" style={{ color: accent, marginBottom: 18, fontSize: 11, letterSpacing: "0.3em" }}>PROPUESTA DE VALOR</div>
        <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 44px)", fontWeight: 700, color: "var(--ink)", marginBottom: 40, letterSpacing: "-0.005em", lineHeight: 1.15 }}>
          Un Enfoque Diferente en Medicina Estética
        </h2>
        <div style={{ marginBottom: 48 }}>
          <Placeholder tone="pink" ratio="21/9" kind="detail" style={{ borderRadius: 6 }} />
        </div>
        <div className="grid-3" style={{ textAlign: "center" }}>
          {items.map((b, i) => (
            <div key={i} style={{ display: "flex", flexDirection: "column", gap: 10, alignItems: "center" }}>
              <div style={{ color: accent, marginBottom: 6 }}><Icon name={b.icon} size={26} color={accent} /></div>
              <h3 className="display-bold" style={{ fontSize: 16, fontWeight: 700, color: "var(--ink)" }}>{b.title}</h3>
              <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--ink-soft)" }}>{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

Object.assign(window, { Nav, Hero, Benefits, PinkCTA });
