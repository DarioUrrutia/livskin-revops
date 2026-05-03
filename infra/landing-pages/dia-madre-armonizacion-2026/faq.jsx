// ============== FAQ — preguntas frecuentes ==============
const FAQ = ({ accent }) => {
  const items = [
    {
      q: "¿El Botox se nota? ¿Voy a perder mis expresiones?",
      a: "No, si está bien aplicado. Trabajamos con microdosis y puntos precisos para suavizar líneas sin congelar el rostro. Sigues moviéndote, sigues expresándote. Solo se ve más descansado."
    },
    {
      q: "¿En cuánto tiempo veo el resultado y cuánto dura?",
      a: "El efecto comienza a notarse entre el día 3 y 5, y se asienta por completo a los 14 días. La duración promedio es de 4 a 6 meses, dependiendo del metabolismo de cada paciente y la zona aplicada."
    },
    {
      q: "¿Es doloroso? ¿Necesito reposo después?",
      a: "Las microinyecciones son rápidas y muy tolerables. Aplicamos frío local y, si lo prefieres, anestesia tópica. La sesión dura 15 a 20 minutos y puedes retomar tu día con normalidad. Solo evitamos ejercicio intenso y masajes faciales por 24 horas."
    },
    {
      q: "¿Desde qué edad se recomienda?",
      a: "No hay una edad fija. Lo evaluamos por la calidad de la piel, la dinámica muscular y los objetivos personales. En algunos casos se aplica de forma preventiva desde los 28–30, en otros como tratamiento correctivo más adelante. Lo definimos en la evaluación."
    },
    {
      q: "¿Qué producto usan?",
      a: "Trabajamos exclusivamente con toxina botulínica original aprobada por DIGEMID, de laboratorios certificados. La aplicación la realiza un médico especialista, en un ambiente clínico controlado."
    },
    {
      q: "¿Tiene riesgos o efectos secundarios?",
      a: "Aplicado por un médico con criterio, es uno de los procedimientos estéticos más seguros. Puede haber un leve enrojecimiento o pequeños hematomas que desaparecen en horas. Por eso la evaluación previa no es opcional: define qué se aplica, dónde y cuánto."
    },
    {
      q: "¿Puedo combinarlo con otros tratamientos?",
      a: "Sí. El Botox suele combinarse con ácido hialurónico, bioestimuladores o skinbooster según la armonización que tu rostro requiera. Esa combinación se decide en la evaluación, no antes."
    },
    {
      q: "¿Cuánto cuesta?",
      a: "El precio depende de las zonas a tratar y la cantidad de unidades necesarias. Por eso no damos un monto único en redes: te lo confirmamos en la evaluación, que es sin costo y sin compromiso."
    },
  ];

  const [open, setOpen] = React.useState(0);

  return (
    <section id="faq" className="sec" style={{ background: "var(--bg)" }}>
      <div style={{ maxWidth: 880, margin: "0 auto", padding: "0 var(--sp-x)" }}>
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <div className="eyebrow" style={{ color: accent, marginBottom: 14, fontSize: 11, letterSpacing: "0.3em" }}>RESUELVE TUS DUDAS</div>
          <h2 className="display-bold" style={{ fontSize: "clamp(26px, 5vw, 42px)", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.005em", lineHeight: 1.15, marginBottom: 14 }}>
            Preguntas frecuentes
          </h2>
          <p style={{ fontSize: "clamp(13px, 2vw, 14.5px)", color: "var(--ink-soft)", lineHeight: 1.7, maxWidth: 560, margin: "0 auto" }}>
            Todo lo que normalmente nos preguntan antes de la primera evaluación.
          </p>
        </div>

        <div style={{ borderTop: "1px solid var(--line)" }}>
          {items.map((it, i) => {
            const isOpen = open === i;
            return (
              <div key={i} style={{ borderBottom: "1px solid var(--line)" }}>
                <button
                  onClick={() => setOpen(isOpen ? -1 : i)}
                  style={{
                    width: "100%", textAlign: "left", padding: "26px 0",
                    background: "transparent", border: "none", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24,
                  }}
                >
                  <span className="display-bold" style={{
                    fontSize: "clamp(15px, 2.4vw, 18px)",
                    fontWeight: 600, color: "var(--ink)", lineHeight: 1.4,
                    letterSpacing: "-0.005em",
                  }}>{it.q}</span>
                  <span style={{
                    flexShrink: 0, width: 28, height: 28, borderRadius: 999,
                    border: `1px solid ${isOpen ? accent : "var(--line)"}`,
                    background: isOpen ? accent : "transparent",
                    color: isOpen ? "#FFF" : "var(--ink)",
                    display: "inline-flex", alignItems: "center", justifyContent: "center",
                    fontSize: 18, fontWeight: 300, lineHeight: 1,
                    transition: "all .3s cubic-bezier(.65,0,.35,1)",
                    transform: isOpen ? "rotate(45deg)" : "rotate(0)",
                  }}>+</span>
                </button>
                <div style={{
                  maxHeight: isOpen ? 400 : 0, overflow: "hidden",
                  transition: "max-height .45s cubic-bezier(.65,0,.35,1)",
                }}>
                  <p style={{
                    fontSize: "clamp(14px, 2vw, 15px)", lineHeight: 1.75,
                    color: "var(--ink-soft)", maxWidth: 680,
                    paddingBottom: 26,
                  }}>{it.a}</p>
                </div>
              </div>
            );
          })}
        </div>

        <p style={{
          textAlign: "center", marginTop: 48,
          fontSize: 13, color: "var(--ink-soft)",
        }}>
          ¿Tu pregunta no está aquí?{" "}
          <a href="#reservar" style={{ color: "var(--ink)", borderBottom: `1px solid ${accent}`, paddingBottom: 2 }}>
            Conversemos en la evaluación →
          </a>
        </p>
      </div>
    </section>
  );
};

Object.assign(window, { FAQ });
