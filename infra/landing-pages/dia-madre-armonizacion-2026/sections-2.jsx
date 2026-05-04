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

// ============== ANTES / DESPUÉS — slider individual ==============
const BeforeAfterSlider = ({ before, after, caption, accent }) => {
  const [pos, setPos] = React.useState(50);
  const ref = React.useRef(null);
  const dragging = React.useRef(false);
  const handleMove = (x) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    setPos(Math.max(0, Math.min(100, ((x - r.left) / r.width) * 100)));
  };
  React.useEffect(() => {
    const up = () => (dragging.current = false);
    const mv = (e) => { if (dragging.current) handleMove(e.clientX || (e.touches && e.touches[0].clientX)); };
    window.addEventListener("mouseup", up); window.addEventListener("touchend", up);
    window.addEventListener("mousemove", mv); window.addEventListener("touchmove", mv);
    return () => {
      window.removeEventListener("mouseup", up); window.removeEventListener("touchend", up);
      window.removeEventListener("mousemove", mv); window.removeEventListener("touchmove", mv);
    };
  }, []);
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <div ref={ref}
        onMouseDown={(e) => { dragging.current = true; handleMove(e.clientX); }}
        onTouchStart={(e) => { dragging.current = true; handleMove(e.touches[0].clientX); }}
        style={{ position: "relative", aspectRatio: "4/5", overflow: "hidden", cursor: "ew-resize", userSelect: "none", borderRadius: 8, boxShadow: "0 20px 50px -25px rgba(0,0,0,0.18)", touchAction: "none", width: "100%", maxWidth: 540 }}>
        <div style={{ position: "absolute", inset: 0 }}>
          <img src={after} alt="Después" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          <div className="eyebrow" style={{ position: "absolute", left: 14, top: 14, padding: "5px 10px", background: "var(--ink)", color: "#FFF", fontSize: 9, borderRadius: 999 }}>Después</div>
        </div>
        <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
          <img src={before} alt="Antes" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          <div className="eyebrow" style={{ position: "absolute", left: 14, top: 14, padding: "5px 10px", background: "rgba(255,255,255,0.92)", color: "var(--ink)", fontSize: 9, borderRadius: 999 }}>Antes</div>
        </div>
        <div style={{ position: "absolute", top: 0, bottom: 0, left: `${pos}%`, width: 2, background: "#FFF", boxShadow: "0 0 12px rgba(0,0,0,0.2)", transform: "translateX(-1px)" }}>
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: 44, height: 44, borderRadius: "50%", background: "#FFF", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 6px 20px rgba(0,0,0,0.25)" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={accent} strokeWidth="1.5" strokeLinecap="round"><path d="M9 6l-5 6 5 6M15 6l5 6-5 6"/></svg>
          </div>
        </div>
      </div>
      {caption && (
        <p className="eyebrow" style={{ fontSize: 10.5, letterSpacing: "0.22em", color: "var(--ink-mute)" }}>
          {caption}
        </p>
      )}
    </div>
  );
};

// ============== ANTES / DESPUÉS — sección completa con múltiples casos ==============
const BeforeAfter = ({ accent }) => {
  const cases = [
    { before: "images/antes.jpg",   after: "images/despues.jpg",   caption: "Caso 1 · Armonización integral" },
    { before: "images/antes-2.jpg", after: "images/despues-2.jpg", caption: "Caso 2 · Definición de líneas" },
    { before: "images/antes-3.jpg", after: "images/despues-3.jpg", caption: "Caso 3 · Armonización de frente" },
  ];
  return (
    <section id="resultados" className="sec" style={{ background: "var(--bg-pink)" }}>
      <style>{`
        .ba-grid { display: grid; grid-template-columns: 1fr; gap: 48px; max-width: 540px; margin: 0 auto; }
        @media (min-width: 900px) { .ba-grid { grid-template-columns: repeat(2, 1fr); max-width: 1140px; gap: 40px; } }
        @media (min-width: 1280px) { .ba-grid { grid-template-columns: repeat(3, 1fr); max-width: 1400px; gap: 36px; } }
      `}</style>
      <div style={{ maxWidth: 1400, margin: "0 auto", textAlign: "center" }}>
        <div className="eyebrow" style={{ color: accent, marginBottom: 16, fontSize: 11, letterSpacing: "0.3em" }}>NATURALIDAD QUE SE NOTA SIN NOTARSE</div>
        <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 44px)", fontWeight: 700, marginBottom: 12, letterSpacing: "-0.005em", color: "var(--ink)", lineHeight: 1.15 }}>Sigues siendo tú.</h2>
        <p style={{ fontSize: "clamp(13px, 2vw, 15px)", color: "var(--ink-soft)", marginBottom: 48, maxWidth: 620, marginLeft: "auto", marginRight: "auto", lineHeight: 1.7 }}>
          Desliza cada imagen para ver el cambio. La diferencia está en cómo te sientes, no en cómo te ves.
        </p>
        <div className="ba-grid">
          {cases.map((c, i) => (
            <BeforeAfterSlider key={i} before={c.before} after={c.after} caption={c.caption} accent={accent} />
          ))}
        </div>
      </div>
    </section>
  );
};

// ============== PROCESO ==============
const Process = ({ accent }) => {
  const steps = [
    { n: "01", title: "Conversamos",  desc: "Antes de cualquier evaluación, escuchamos lo que buscas y lo que no." },
    { n: "02", title: "Evaluamos",    desc: "Analizamos tu rostro como un todo. Tu estructura, tu expresión, tu identidad." },
    { n: "03", title: "Decides tú",   desc: "Te explicamos opciones reales. Tú eliges el ritmo y la dirección." },
    { n: "04", title: "Acompañamos",  desc: "Seguimiento a los 14 días. Tu criterio guía cada ajuste." },
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
        <div className="eyebrow" style={{ color: accent, marginBottom: 16, fontSize: 11, letterSpacing: "0.3em" }}>CADA ROSTRO TIENE SU PROPIA FORMA</div>
        <h2 className="display-bold" style={{ fontSize: "clamp(28px, 6vw, 52px)", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.005em", marginBottom: 18, lineHeight: 1.15 }}>
          La armonización<br/>es una decisión personal.
        </h2>
        <p style={{ maxWidth: 640, margin: "0 auto", fontSize: "clamp(13px, 2vw, 14px)", color: "var(--ink-soft)", lineHeight: 1.7 }}>
          No existe una fórmula. Por eso evaluamos cada rostro como único, y te acompañamos a definir tu propio criterio antes que cualquier procedimiento.
        </p>
      </section>
      <section id="proceso" className="sec" style={{ background: "#FFFFFF", color: "var(--ink)" }}>
        <div style={{ maxWidth: 1180, margin: "0 auto", textAlign: "center", marginBottom: 48 }}>
          <div className="eyebrow" style={{ color: accent, marginBottom: 14, fontSize: 11, letterSpacing: "0.32em" }}>SOBRE EL TRATAMIENTO</div>
          <h2 className="display-bold" style={{ fontSize: "clamp(24px, 4.5vw, 38px)", fontWeight: 700, letterSpacing: "0.02em", marginBottom: 16, color: "var(--ink)" }}>LA ARMONIZACIÓN FACIAL, EXPLICADA CON CRITERIO.</h2>
          <p style={{ maxWidth: 620, margin: "0 auto", fontSize: "clamp(13px, 2vw, 14.5px)", color: "var(--ink-soft)", lineHeight: 1.75 }}>
            Combinación de ácido hialurónico y toxina botulínica, definida según tu rostro. No es una fórmula estándar: evaluamos estructura, expresión y proporciones para decidir qué aplicar, dónde y cuánto. Productos originales, sesión personalizada, resultado natural. Sin congelar, sin perder tu expresión.
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
            <div className="display-bold" style={{ fontSize: 11, color: accent, letterSpacing: "0.28em", marginBottom: 10 }}>EDICIÓN DÍA DE LA MADRE</div>
            <h3 className="display-bold" style={{ fontSize: "clamp(18px, 3.5vw, 22px)", fontWeight: 700, marginBottom: 20, color: "var(--ink)", lineHeight: 1.3 }}>Este mayo, regálate una decisión.</h3>
            <window.PinkCTA href="#reservar" size="md">Explora tu enfoque</window.PinkCTA>
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
    { quote: "Me gustó que no me ofrecieran algo por ofrecer. Evaluaron mi rostro y me recomendaron lo que realmente necesitaba. Se nota el cambio, pero sigo viéndome yo.", name: "MARYORI" },
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
// phone interno = 9 dígitos sin prefijo (ej: "980727888")
// formato display = "980 727 888"
// formato canónico (WA + sistema) = "+51 980 727 888"
const formatPhoneDisplay = (digits) => {
  if (!digits) return "";
  const a = digits.slice(0, 3);
  const b = digits.slice(3, 6);
  const c = digits.slice(6, 9);
  return [a, b, c].filter(Boolean).join(" ");
};

const Booking = ({ accent }) => {
  const [name, setName] = React.useState("");
  const [phone, setPhone] = React.useState(""); // solo dígitos, max 9
  const [email, setEmail] = React.useState("");
  const [consent, setConsent] = React.useState(false);
  const [touched, setTouched] = React.useState(false);

  const nameOk = name.trim().length >= 2;
  const phoneOk = /^9\d{8}$/.test(phone); // móvil Perú: 9 dígitos empezando con 9
  const canSubmit = nameOk && phoneOk && consent;

  const phoneCanonical = phone ? `+51 ${formatPhoneDisplay(phone)}` : "[tel]";
  const waText = `Hola Livskin, soy ${name || "[nombre]"}, mi número es ${phoneCanonical}${email ? `, email: ${email}` : ""}. Me gustaría agendar una valoración de Armonización Facial.`;
  const waLink = window.getWALink ? window.getWALink(waText) : `https://wa.me/51980727888?text=${encodeURIComponent(waText)}`;

  const handleClick = (e) => {
    if (!canSubmit) {
      e.preventDefault();
      setTouched(true);
    }
  };

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
          <div className="eyebrow" style={{ color: accent, marginBottom: 14, fontSize: 11, letterSpacing: "0.3em" }}>EDICIÓN DÍA DE LA MADRE · MAYO</div>
          <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 42px)", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.005em", marginBottom: 16, lineHeight: 1.15 }}>Agenda tu evaluación de Armonización Facial.</h2>
          <p style={{ fontSize: "clamp(13px, 2vw, 14.5px)", color: "var(--ink-soft)", marginBottom: 22, lineHeight: 1.7 }}>Una conversación con criterio profesional antes de cualquier aplicación. Sin compromiso, sin presión.</p>
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
            <Field label="Nombres" value={name} onChange={setName} required error={touched && !nameOk} />
            <PhoneField label="Teléfono móvil" value={phone} onChange={setPhone} required error={touched && !phoneOk} />
            <Field label="Email" hint="(opcional)" value={email} onChange={setEmail} type="email" />

            <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginTop: 4 }}>
              <input
                id="consent"
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                style={{ marginTop: 4, width: 16, height: 16, accentColor: accent, flexShrink: 0, cursor: "pointer" }}
              />
              <label htmlFor="consent" style={{
                fontSize: 12.5, lineHeight: 1.55, color: "var(--ink-soft)", cursor: "pointer",
                fontFamily: "'Open Sans', sans-serif",
              }}>
                Acepto que Livskin me contacte por WhatsApp o teléfono para coordinar mi evaluación. He leído y acepto la{" "}
                <a href="legal/privacidad.html" target="_blank" rel="noopener" style={{ color: "var(--ink)", borderBottom: `1px solid ${accent}` }}>Política de Privacidad</a>{" "}y los{" "}
                <a href="legal/terminos.html" target="_blank" rel="noopener" style={{ color: "var(--ink)", borderBottom: `1px solid ${accent}` }}>Términos y Condiciones</a>.
              </label>
            </div>

            {touched && !canSubmit && (
              <div style={{ fontSize: 12, color: "#B91C1C", lineHeight: 1.5, marginTop: -4 }}>
                {!nameOk && <div>• Necesitamos tu nombre.</div>}
                {!phoneOk && <div>• Necesitamos un teléfono válido.</div>}
                {!consent && <div>• Debes aceptar la política de privacidad para continuar.</div>}
              </div>
            )}

            <window.PinkCTA
              href={canSubmit ? waLink : "#"}
              target={canSubmit ? "_blank" : undefined}
              rel={canSubmit ? "noreferrer" : undefined}
              onClick={handleClick}
              size="lg"
              style={{ marginTop: 6, opacity: canSubmit ? 1 : 0.55 }}
            >
              <Icon name="wa" size={15} color="#FFF" /> Agendar evaluación
            </window.PinkCTA>

            <p style={{ fontSize: 11.5, color: "var(--ink-mute)", lineHeight: 1.6, marginTop: 4, textAlign: "center" }}>
              Tus datos solo se usan para coordinar tu cita. No los compartimos con terceros.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

const PhoneField = ({ label, value, onChange, required, error }) => {
  const display = formatPhoneDisplay(value);
  const handleChange = (e) => {
    const digits = e.target.value.replace(/\D/g, "").slice(0, 9);
    onChange(digits);
  };
  return (
    <div>
      <label style={{ display: "block", fontSize: 13, color: "var(--ink)", marginBottom: 8, fontWeight: 600 }}>
        {label}
      </label>
      <div style={{
        display: "flex", alignItems: "stretch",
        border: `1px solid ${error ? "#B91C1C" : "var(--line)"}`,
        borderRadius: 4, background: "#FFF", overflow: "hidden",
      }}>
        <span style={{
          padding: "13px 12px",
          background: "#FAFAFA",
          borderRight: "1px solid var(--line)",
          fontFamily: "'Open Sans', sans-serif", fontSize: 15,
          color: "var(--ink-soft)", display: "flex", alignItems: "center",
          letterSpacing: "0.02em", whiteSpace: "nowrap",
        }}>
          🇵🇪 +51
        </span>
        <input
          type="tel"
          inputMode="numeric"
          value={display}
          onChange={handleChange}
          placeholder="999 999 999"
          required={required}
          maxLength={11}
          style={{
            flex: 1, padding: "13px 14px",
            border: "none", background: "transparent",
            fontFamily: "'Open Sans', sans-serif", fontSize: 15,
            color: "var(--ink)", outline: "none",
            letterSpacing: "0.02em",
          }}
        />
      </div>
      {error && (
        <div style={{ fontSize: 11.5, color: "#B91C1C", marginTop: 6, lineHeight: 1.5 }}>
          Ingresa un número móvil de 9 dígitos que empiece con 9.
        </div>
      )}
    </div>
  );
};

const Field = ({ label, value, onChange, placeholder, type = "text", required, hint, error }) => (
  <div>
    <label style={{ display: "block", fontSize: 13, color: "var(--ink)", marginBottom: 8, fontWeight: 600 }}>
      {label}
      {hint && <span style={{ fontWeight: 400, color: "var(--ink-mute)", marginLeft: 6, fontSize: 12 }}>{hint}</span>}
    </label>
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      style={{
        width: "100%", padding: "13px 14px",
        border: `1px solid ${error ? "#B91C1C" : "var(--line)"}`,
        borderRadius: 4, background: "#FFF",
        fontFamily: "'Open Sans', sans-serif", fontSize: 15, color: "var(--ink)", outline: "none",
      }}
    />
  </div>
);

// ============== FOOTER ==============
const Footer = () => (
  <footer style={{ padding: "36px 20px 28px", background: "var(--bg)", borderTop: "1px solid var(--line)" }}>
    <style>{`
      .footer-inner { display: flex; flex-direction: column; align-items: center; gap: 22px; text-align: center; }
      @media (min-width: 720px) { .footer-inner { flex-direction: row; justify-content: space-between; text-align: left; align-items: center; } }
      .footer-legal { display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; }
      @media (min-width: 720px) { .footer-legal { justify-content: flex-end; } }
    `}</style>
    <div style={{ maxWidth: 1280, margin: "0 auto" }} className="footer-inner">
      <Logo size={22} showTagline={true} />
      <div className="eyebrow" style={{ fontSize: 10, color: "var(--ink-mute)", letterSpacing: "0.2em" }}>© 2026 LIVSKIN · CUSCO, PERÚ</div>
      <div className="footer-legal">
        <a href="https://www.instagram.com/livskin.peru/" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>Instagram</a>
        <a href="https://www.facebook.com/livskinperu" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>Facebook</a>
        <a href="https://wa.me/51980727888" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>WhatsApp</a>
        <span style={{ color: "var(--line)" }}>·</span>
        <a href="legal/privacidad.html" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>Privacidad</a>
        <a href="legal/terminos.html" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>Términos</a>
        <a href="legal/cookies.html" target="_blank" rel="noopener" className="eyebrow" style={{ fontSize: 10, color: "var(--ink-soft)", letterSpacing: "0.2em" }}>Cookies</a>
      </div>
    </div>
  </footer>
);

const WAFloat = () => {
  const href = window.getWALink ? window.getWALink() : "https://wa.me/51980727888";
  return (
    <a href={href} target="_blank" rel="noreferrer" style={{ position: "fixed", right: 18, bottom: 18, zIndex: 40, width: 54, height: 54, borderRadius: "50%", background: "#25D366", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 14px 30px -10px rgba(37,211,102,0.5)", color: "#FFF" }}>
      <Icon name="wa" size={24} color="#FFF" />
    </a>
  );
};

Object.assign(window, { BeforeAfter, Process, Booking, Testimonials, Footer, WAFloat, Marquee: () => null });
