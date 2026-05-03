// ============== FAQ — preguntas frecuentes ==============
const FAQ = ({ accent }) => {
  const items = [
    {
      q: "¿Qué es la Armonización Facial?",
      a: "Es un enfoque médico que combina ácido hialurónico y toxina botulínica para mejorar la proporción y expresión del rostro de forma natural. No es un tratamiento estándar: cada plan se define después de evaluar tu estructura facial, tu dinámica muscular y lo que tú buscas. El objetivo no es transformarte, es que tu rostro se vea más en armonía consigo mismo."
    },
    {
      q: "¿Se va a notar? ¿Voy a perder mis expresiones?",
      a: "No, si está bien aplicada. Trabajamos con microdosis y puntos precisos: el ácido hialurónico aporta volumen donde tu rostro lo necesita, y la toxina botulínica suaviza líneas sin congelar la expresión. Sigues moviéndote, sigues expresándote. La gente nota que estás distinta, pero no sabe exactamente qué."
    },
    {
      q: "¿En cuánto tiempo veo el resultado y cuánto dura?",
      a: "El ácido hialurónico se ve desde el primer día y se asienta entre la primera y segunda semana; dura de 9 a 18 meses según la zona. La toxina botulínica empieza a notarse entre el día 3 y 5, y se asienta a los 14 días; dura de 4 a 6 meses. Es normal que ambos componentes se combinen en un plan que se ajusta con el tiempo."
    },
    {
      q: "¿Es doloroso? ¿Necesito reposo después?",
      a: "Las microinyecciones son tolerables. Aplicamos anestesia tópica antes de empezar y frío local durante el procedimiento. La sesión completa dura entre 30 y 60 minutos según las zonas a trabajar. Puedes retomar tu día con normalidad; solo evitamos ejercicio intenso, masajes faciales y exposición al sol fuerte por 24 a 48 horas."
    },
    {
      q: "¿Desde qué edad se recomienda?",
      a: "No hay una edad fija. Lo evaluamos por la calidad de tu piel, tu dinámica muscular y tus objetivos. En algunos casos se trabaja de forma preventiva desde los 28–30, en otros como armonización correctiva más adelante. Lo definimos contigo en la evaluación."
    },
    {
      q: "¿Qué productos usan?",
      a: "Trabajamos exclusivamente con productos originales aprobados por DIGEMID: ácido hialurónico de marcas reconocidas mundialmente y toxina botulínica de laboratorios certificados. Cada caja viene con su número de lote y su trazabilidad — puedes verla antes de la aplicación. El procedimiento lo realiza un médico especialista en un ambiente clínico controlado."
    },
    {
      q: "¿Tiene riesgos o efectos secundarios?",
      a: "Aplicada por un médico con criterio, es uno de los procedimientos estéticos más seguros. Puede haber leve enrojecimiento, pequeña inflamación o hematomas que desaparecen en horas o pocos días. Por eso la evaluación previa no es opcional: define qué se aplica, dónde, cuánto y si hay algo que contraindique el procedimiento ese día."
    },
    {
      q: "¿Cuánto cuesta?",
      a: "El precio depende de las zonas a trabajar, las unidades necesarias y los productos que usemos. Por eso no damos un monto único en redes: te lo confirmamos en la evaluación, que es sin costo y sin compromiso. Tú decides hasta dónde avanzar y a qué ritmo."
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
