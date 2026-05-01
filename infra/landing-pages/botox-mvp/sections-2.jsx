// ============== TIME PILL ==============
const TimePill = ({ label, active, onClick }) => {
  const [hover, setHover] = React.useState(false);
  const PINK = "#F4A6BB";
  const BLUE = "#5BB5D6";
  const bg = active ? PINK : hover ? BLUE : "#FFF";
  const fg = active || hover ? "#FFF" : "var(--ink)";
  const border = active ? PINK : hover ? BLUE : "var(--line)";
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        flex: 1, padding: "14px 8px",
        border: `1px solid ${border}`,
        background: bg, color: fg,
        borderRadius: 999,
        fontFamily: "Montserrat, sans-serif", fontWeight: 600,
        fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase",
        cursor: "pointer",
        transition: "all .25s cubic-bezier(.65,0,.35,1)",
      }}
    >
      {label}
    </button>
  );
};

// ============== ANTES / DESPUÉS ==============
const BeforeAfter = ({ accent }) => {
  const [pos, setPos] = React.useState(50);
  const ref = React.useRef(null);
  const dragging = React.useRef(false);
  const handleMove = (x) => { if (!ref.current) return; const r = ref.current.getBoundingClientRect(); setPos(Math.max(0, Math.min(100, ((x - r.left) / r.width) * 100))); };
  React.useEffect(() => {
    const up = () => (dragging.current = false);
    const mv = (e) => { if (dragging.current) handleMove(e.clientX || (e.touches && e.touches[0].clientX)); };
    window.addEventListener("mouseup", up); window.addEventListener("touchend", up);
    window.addEventListener("mousemove", mv); window.addEventListener("touchmove", mv);
    return () => { window.removeEventListener("mouseup", up); window.removeEventListener("touchend", up); window.removeEventListener("mousemove", mv); window.removeEventListener("touchmove", mv); };
  }, []);
  return (
    <section id="resultados" className="sec" style={{ background: "var(--bg)" }}>
      <div style={{ maxWidth: 1180, margin: "0 auto", textAlign: "center" }}>
        <div className="eyebrow" style={{ color: accent, marginBottom: 16, fontSize: 11, letterSpacing: "0.3em" }}>RESULTADOS REALES</div>
        <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 44px)", fontWeight: 700, marginBottom: 12, letterSpacing: "-0.005em", color: "var(--ink)", lineHeight: 1.15 }}>Antes &amp; después</h2>
        <p style={{ fontSize: "clamp(13px, 2vw, 15px)", color: "var(--ink-soft)", marginBottom: 40 }}>Desliza para ver el cambio. Una sola sesión, dos semanas después.</p>
        <div ref={ref}
          onMouseDown={(e) => { dragging.current = true; handleMove(e.clientX); }}
          onTouchStart={(e) => { dragging.current = true; handleMove(e.touches[0].clientX); }}
          style={{ position: "relative", aspectRatio: "16/10", overflow: "hidden", cursor: "ew-resize", userSelect: "none", borderRadius: 8, boxShadow: "0 20px 50px -25px rgba(0,0,0,0.18)", touchAction: "none" }}>
          <div style={{ position: "absolute", inset: 0 }}>
            <Placeholder tone="pink" ratio="16/10" kind="portrait" />
            <div className="eyebrow" style={{ position: "absolute", left: 14, top: 14, padding: "5px 10px", background: "var(--ink)", color: "#FFF", fontSize: 9, borderRadius: 999 }}>Después</div>
          </div>
          <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
            <Placeholder tone="pink" ratio="16/10" kind="detail" />
            <div className="eyebrow" style={{ position: "absolute", left: 14, top: 14, padding: "5px 10px", background: "rgba(255,255,255,0.92)", color: "var(--ink)", fontSize: 9, borderRadius: 999 }}>Antes</div>
          </div>
          <div style={{ position: "absolute", top: 0, bottom: 0, left: `${pos}%`, width: 2, background: "#FFF", boxShadow: "0 0 12px rgba(0,0,0,0.2)", transform: "translateX(-1px)" }}>
            <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: 44, height: 44, borderRadius: "50%", background: "#FFF", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 6px 20px rgba(0,0,0,0.25)" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={accent} strokeWidth="1.5" strokeLinecap="round"><path d="M9 6l-5 6 5 6M15 6l5 6-5 6"/></svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============== PROCESO ==============
const Process = ({ accent }) => {
  const steps = [
    { n: "01", title: "Valoración", desc: "Evaluamos tu rostro de forma integral antes de cualquier aplicación." },
    { n: "02", title: "Plan a medida", desc: "Diseñamos un plan que respeta tu estructura y expresión natural." },
    { n: "03", title: "Aplicación", desc: "Microinyecciones precisas con producto original. 15–20 min, sin baja." },
    { n: "04", title: "Seguimiento", desc: "Revisión a los 14 días para confirmar resultado y retoque si fuera necesario." },
  ];
  return (
    <>
      <style>{`
        .proceso-grid { display: grid; grid-template-columns: 1fr; gap: 14px; }
        @media (min-width: 720px) { .proceso-grid { grid-template-columns: 1fr 1fr; gap: 20px; } }
        .proceso-card { padding: 28px 24px; }
        @media (min-width: 720px) { .proceso-card { padding: 36px 34px; } }
      `}</style>
      <section className="sec-tight" style={{ background: "var(--bg-pink)", textAlign: "center" }}>
        <div className="eyebrow" style={{ color: accent, marginBottom: 16, fontSize: 11, letterSpacing: "0.3em" }}>NO TRABAJAMOS SOLO TRATAMIENTOS.</div>
        <h2 className="display-bold" style={{ fontSize: "clamp(28px, 6vw, 52px)", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.005em", marginBottom: 18, lineHeight: 1.15 }}>
          Trabajamos<br/>Armonización Facial.
        </h2>
        <p style={{ maxWidth: 640, margin: "0 auto", fontSize: "clamp(13px, 2vw, 14px)", color: "var(--ink-soft)", lineHeight: 1.7 }}>
          Tratar una sola zona no logra un resultado realmente armónico. Por eso evaluamos el rostro de forma completa
          y recomendamos la mejor combinación de tratamientos según cada paciente.
        </p>
      </section>
      <section id="proceso" className="sec" style={{ background: "#FFFFFF", color: "var(--ink)" }}>
        <div style={{ maxWidth: 1180, margin: "0 auto", textAlign: "center", marginBottom: 48 }}>
          <div className="eyebrow" style={{ color: accent, marginBottom: 14, fontSize: 11, letterSpacing: "0.32em" }}>CONOCE MÁS DE NUESTRO</div>
          <h2 className="display-bold" style={{ fontSize: "clamp(24px, 4.5vw, 38px)", fontWeight: 700, letterSpacing: "0.02em", marginBottom: 16, color: "var(--ink)" }}>TRATAMIENTO DE BOTOX</h2>
          <p style={{ maxWidth: 560, margin: "0 auto", fontSize: "clamp(13px, 2vw, 14px)", color: "var(--ink-soft)", lineHeight: 1.7 }}>
            Cada rostro es único. Por eso diseñamos planes adaptados a tu estructura, expresividad y objetivos.
          </p>
        </div>
        <div className="proceso-grid" style={{ maxWidth: 1180, margin: "0 auto" }}>
          {steps.map((s, i) => (
            <div key={i} className="proceso-card" style={{
              background: "#FFFFFF",
              border: "1px solid #F0E6EA",
              borderRadius: 8,
              boxShadow: "0 1px 2px rgba(244,166,187,0.04), 0 8px 24px -16px rgba(244,166,187,0.15)",
              textAlign: "center",
            }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{
                  width: 34, height: 34, borderRadius: "50%",
                  background: "var(--brand-pink-soft)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: "Montserrat, sans-serif", fontWeight: 700,
                  fontSize: 12, color: accent, letterSpacing: "0.04em", flexShrink: 0,
                }}>{s.n}</div>
                <h3 className="display-bold" style={{ fontSize: 17, fontWeight: 700, color: "var(--ink)" }}>{s.title}</h3>
              </div>
              <p style={{ fontSize: 13.5, lineHeight: 1.75, color: "var(--ink-soft)" }}>{s.desc}</p>
            </div>
          ))}
          <div style={{
            gridColumn: "1 / -1",
            marginTop: 14,
            padding: "32px 24px",
            textAlign: "center",
            background: "var(--brand-pink-soft)",
            borderRadius: 8,
          }}>
            <div className="display-bold" style={{ fontSize: 11, color: accent, letterSpacing: "0.28em", marginBottom: 10 }}>¿CUÁL ES LA MEJOR OPCIÓN PARA TI?</div>
            <h3 className="display-bold" style={{ fontSize: "clamp(18px, 3.5vw, 22px)", fontWeight: 700, marginBottom: 20, color: "var(--ink)", lineHeight: 1.3 }}>Cada paciente requiere un enfoque distinto.</h3>
            <window.PinkCTA href="#reservar" size="md">Agendar evaluación</window.PinkCTA>
          </div>
        </div>
      </section>
    </>
  );
};

// ============== TESTIMONIALS ==============
const Testimonials = ({ accent }) => {
  const items = [
    { quote: "Yo inicialmente quería hacerme solo botox, pero en la evaluación me explicaron que lo mejor era trabajar la armonización facial. Al final decidí hacerlo así y el resultado fue mucho más natural y completo. Valió totalmente la pena.", name: "BRENDA" },
    { quote: "Me gustó que no me ofrecieran algo por ofrecer. Evaluaron mi rostro y me recomendaron lo que realmente necesitaba. Se nota el cambio, pero sigo viéndome yo.", name: "MARYORI", role: "San Francisco" },
  ];
  return (
    <section className="sec" style={{ background: "var(--bg)" }}>
      <div style={{ maxWidth: 720, margin: "0 auto", display: "flex", flexDirection: "column", gap: 56 }}>
        {items.map((t, i) => (
          <div key={i} style={{ textAlign: "center" }}>
            <div className="display-bold" style={{ fontSize: 36, color: "#D4D0CC", lineHeight: 1, marginBottom: 18 }}>"</div>
            <p style={{ fontSize: "clamp(14px, 2.2vw, 15px)", lineHeight: 1.85, color: "var(--ink-soft)", marginBottom: 22, fontFamily: "Montserrat, sans-serif", fontWeight: 500 }}>
              {t.quote}
            </p>
            <div style={{ width: 30, height: 30, borderRadius: "50%", background: "var(--brand-pink-soft)", margin: "0 auto 10px" }} />
            <div className="display-bold" style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.3em", color: "var(--ink)" }}>{t.name}</div>
            {t.role && <div style={{ fontSize: 11, color: "var(--ink-mute)", marginTop: 4, letterSpacing: "0.06em" }}>{t.role}</div>}
          </div>
        ))}
      </div>
    </section>
  );
};

// ============== RESERVAR ==============
const Booking = ({ accent }) => {
  const [name, setName] = React.useState(""); const [phone, setPhone] = React.useState(""); const [email, setEmail] = React.useState(""); const [time, setTime] = React.useState("Mañana");
  const waLink = `https://wa.me/51980727888?text=${encodeURIComponent(`Hola Livskin, soy ${name || "[nombre]"}, mi número es ${phone || "[tel]"}, email: ${email || "[email]"}. Me gustaría agendar una valoración de Botox en horario de ${time}.`)}`;
  return (
    <section id="reservar" className="sec" style={{ background: "var(--bg-pink)" }}>
      <style>{`
        .booking-grid { display: grid; grid-template-columns: 1fr; gap: 36px; }
        @media (min-width: 900px) { .booking-grid { grid-template-columns: 1fr 1fr; gap: 60px; } }
        .booking-card { padding: 28px 22px; border-radius: 6px; background: #FFF; }
        @media (min-width: 720px) { .booking-card { padding: 40px 36px; } }
        .info-grid { display: grid; grid-template-columns: 1fr; gap: 22px; }
        @media (min-width: 480px) { .info-grid { grid-template-columns: 1fr 1fr; } }
      `}</style>
      <div style={{ maxWidth: 1100, margin: "0 auto" }} className="booking-grid">
        <div>
          <div className="eyebrow" style={{ color: accent, marginBottom: 14, fontSize: 11, letterSpacing: "0.3em" }}>DA EL SIGUIENTE PASO</div>
          <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 42px)", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.005em", marginBottom: 16, lineHeight: 1.15 }}>Agenda tu evaluación</h2>
          <p style={{ fontSize: "clamp(13px, 2vw, 14px)", color: "var(--ink-soft)", marginBottom: 22 }}>Resultados naturales empiezan con una buena evaluación.</p>
          <a href="#" style={{ display: "inline-block", borderBottom: "1.5px solid var(--ink)", color: "var(--ink)", paddingBottom: 4, fontSize: 13, fontWeight: 600, fontFamily: "Montserrat, sans-serif", marginBottom: 28 }}>Atención previa cita</a>
          <div style={{ display: "flex", flexDirection: "column", gap: 22, marginTop: 24 }}>
            <div>
              <div className="display-bold" style={{ fontSize: 11, color: accent, letterSpacing: "0.2em", marginBottom: 8 }}>📍 UBICACIÓN</div>
              <div style={{ fontSize: 13, color: "var(--ink-soft)" }}>Urb. La Florida O-7, Wanchaq – Cusco</div>
            </div>
            <div className="info-grid">
              <div>
                <div className="display-bold" style={{ fontSize: 11, color: accent, letterSpacing: "0.2em", marginBottom: 8 }}>🕐 HORARIOS</div>
                <div style={{ fontSize: 13, color: "var(--ink-soft)", lineHeight: 1.8 }}>Lun–Vie: 10am–10pm<br/>Sáb: 9am–12pm</div>
              </div>
              <div>
                <div className="display-bold" style={{ fontSize: 11, color: accent, letterSpacing: "0.2em", marginBottom: 8 }}>✉️ CONTACTO</div>
                <div style={{ fontSize: 13, color: "var(--ink-soft)", lineHeight: 1.8 }}>+51 980 727 888<br/>info@livskin.site</div>
              </div>
            </div>
          </div>
        </div>
        <div className="booking-card">
          <div style={{ width: 30, height: 2, background: accent, marginBottom: 20 }} />
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <Field label="Nombres *" value={name} onChange={setName} />
            <Field label="Email *" value={email} onChange={setEmail} type="email" />
            <Field label="Teléfono *" value={phone} onChange={setPhone} type="tel" />
            <div>
              <label style={{ display: "block", fontSize: 13, color: "var(--ink)", marginBottom: 8, fontWeight: 600 }}>Horario preferido</label>
              <div style={{ display: "flex", gap: 8 }}>
                {["Mañana", "Tarde", "Sábado"].map(t => (
                  <TimePill key={t} label={t} active={time === t} onClick={() => setTime(t)} accent={accent} />
                ))}
              </div>
            </div>
            <window.PinkCTA href={waLink} target="_blank" rel="noreferrer" size="lg" style={{ marginTop: 6 }}>
              <Icon name="wa" size={15} color="#FFF" /> Agendar cita
            </window.PinkCTA>
          </div>
        </div>
      </div>
    </section>
  );
};

const Field = ({ label, value, onChange, placeholder, type = "text" }) => (
  <div>
    <label style={{ display: "block", fontSize: 13, color: "var(--ink)", marginBottom: 8, fontWeight: 600 }}>{label}</label>
    <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} style={{ width: "100%", padding: "13px 14px", border: "1px solid var(--line)", borderRadius: 4, background: "#FFF", fontFamily: "'Open Sans', sans-serif", fontSize: 15, color: "var(--ink)", outline: "none" }} />
  </div>
);

// ============== FOOTER ==============
const Footer = () => (
  <footer style={{ padding: "36px 20px 28px", background: "var(--bg)", borderTop: "1px solid var(--line)" }}>
    <style>{`
      .footer-inner { display: flex; flex-direction: column; align-items: center; gap: 18px; text-align: center; }
      @media (min-width: 720px) { .footer-inner { flex-direction: row; justify-content: space-between; text-align: left; } }
    `}</style>
    <div style={{ maxWidth: 1280, margin: "0 auto" }} className="footer-inner">
      <Logo size={22} showTagline={true} />
      <div className="eyebrow" style={{ fontSize: 10, color: "var(--ink-mute)", letterSpacing: "0.2em" }}>© 2026 LIVSKIN · CUSCO, PERÚ</div>
      <div style={{ display: "flex", gap: 20 }}>{["Instagram", "Facebook", "WhatsApp"].map(l => <a key={l} href="#" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>{l}</a>)}</div>
    </div>
  </footer>
);

const WAFloat = () => (
  <a href="https://wa.me/51980727888" data-livskin-wa="true" target="_blank" rel="noopener noreferrer" style={{ position: "fixed", right: 18, bottom: 18, zIndex: 40, width: 54, height: 54, borderRadius: "50%", background: "#25D366", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 14px 30px -10px rgba(37,211,102,0.5)", color: "#FFF" }}>
    <Icon name="wa" size={24} color="#FFF" />
  </a>
);

Object.assign(window, { BeforeAfter, Process, Booking, Testimonials, Footer, WAFloat, Marquee: () => null });
