// Tweaks defaults — JSON between markers must stay valid
const TWEAKS_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#F4A6BB",
  "eyebrow": "EDICIÓN DÍA DE LA MADRE",
  "headline": "Este Día de la Madre,\ndecide por ti.",
  "sub": "Una pausa para verte como te ves cuando nadie te mira. Sin permisos, sin explicaciones."
}/*EDITMODE-END*/;

const App = () => {
  const [tweaks, setTweak] = window.useTweaks(TWEAKS_DEFAULTS);
  const accent = tweaks.accent;

  return (
    <div style={{ background: "var(--bg)", color: "var(--ink)" }}>
      <Nav accent={accent} />
      <Hero eyebrow={tweaks.eyebrow} headline={tweaks.headline} sub={tweaks.sub} accent={accent} />
      <Marquee accent={accent} />
      <Benefits accent={accent} />
      <BeforeAfter accent={accent} />
      <Process accent={accent} />
      <Testimonials accent={accent} />
      <window.FAQ accent={accent} />
      <Booking accent={accent} />
      <Footer />
      <WAFloat accent={accent} />

      <window.TweaksPanel title="Tweaks">
        <window.TweakSection title="Color de marca">
          <window.TweakRadio
            label="Acento principal"
            value={tweaks.accent}
            options={[
              { value: "#F4A6BB", label: "Rosa" },
              { value: "#8B1F1F", label: "Rojo" },
              { value: "#5BB5D6", label: "Azul" },
              { value: "#1F1A1A", label: "Tinta" },
            ]}
            onChange={(v) => setTweak("accent", v)}
          />
          <window.TweakColor
            label="Color personalizado"
            value={tweaks.accent}
            onChange={(v) => setTweak("accent", v)}
          />
        </window.TweakSection>

        <window.TweakSection title="Copy del hero">
          <window.TweakText
            label="Eyebrow"
            value={tweaks.eyebrow}
            onChange={(v) => setTweak("eyebrow", v)}
          />
          <window.TweakText
            label="Titular (\\n = salto)"
            multiline
            value={tweaks.headline}
            onChange={(v) => setTweak("headline", v)}
          />
          <window.TweakText
            label="Subtítulo"
            multiline
            value={tweaks.sub}
            onChange={(v) => setTweak("sub", v)}
          />
        </window.TweakSection>
      </window.TweaksPanel>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
