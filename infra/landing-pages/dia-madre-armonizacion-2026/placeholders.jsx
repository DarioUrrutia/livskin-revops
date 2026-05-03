// ============== LOGO ==============
const Logo = ({ size = 40, dark = false, mono = false, showTagline = true }) => {
  const ink = dark ? "#FFFFFF" : "#1A1A1A";
  const tagline = dark ? "rgba(255,255,255,0.7)" : "#5A5552";
  const dot1 = mono ? ink : "#8B1F1F";
  const dot2 = mono ? ink : "#5BB5D6";
  const dot3 = mono ? ink : "#F8C8CC";
  return (
    <div style={{ display: "inline-flex", flexDirection: "column", alignItems: "flex-start", lineHeight: 1 }}>
      <div style={{ display: "flex", gap: size * 0.16, marginBottom: size * 0.18, marginLeft: size * 0.08 }}>
        <span style={{ width: size * 0.32, height: size * 0.32, borderRadius: "50%", background: dot1, display: "inline-block" }} />
        <span style={{ width: size * 0.32, height: size * 0.32, borderRadius: "50%", background: dot2, display: "inline-block" }} />
        <span style={{ width: size * 0.32, height: size * 0.32, borderRadius: "50%", background: dot3, display: "inline-block" }} />
      </div>
      <div className="display-bold" style={{
        fontSize: size * 0.95,
        fontWeight: 600,
        letterSpacing: size * 0.04,
        color: ink,
        lineHeight: 0.9,
      }}>LIVSKIN</div>
      {showTagline && (
        <div style={{
          fontFamily: "Montserrat, sans-serif",
          fontWeight: 400,
          fontSize: size * 0.18,
          letterSpacing: size * 0.018,
          color: tagline,
          marginTop: size * 0.14,
          textTransform: "uppercase",
        }}>Professional Skincare</div>
      )}
    </div>
  );
};

// ============== PLACEHOLDER (brand-aware) ==============
const Placeholder = ({ tone = "pink", label, ratio = "3/4", style = {}, kind = "portrait" }) => {
  const palettes = {
    pink:  ["#FDF5F5", "#F8C8CC", "#D89094"],   // soft brand pink
    blue:  ["#E8F4F9", "#B5DEEC", "#5BB5D6"],   // brand blue
    red:   ["#F2D8D8", "#C46868", "#8B1F1F"],   // brand red, muted
    warm:  ["#FCE8EC", "#F4A6BB", "#E88AA2"],   // pink (was cream — banished)
    cool:  ["#EFF1F4", "#C9D3DA", "#7A8590"],   // cool gray
  };
  const [c1, c2, c3] = palettes[tone] || palettes.pink;
  const id = React.useMemo(() => "ph" + Math.random().toString(36).slice(2, 8), []);

  return (
    <div style={{
      position: "relative",
      width: "100%",
      aspectRatio: ratio,
      borderRadius: 2,
      overflow: "hidden",
      background: c2,
      ...style,
    }}>
      <svg width="100%" height="100%" viewBox="0 0 400 533" preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0 }}>
        <defs>
          <radialGradient id={id + "g"} cx="35%" cy="30%" r="80%">
            <stop offset="0%" stopColor={c1} />
            <stop offset="55%" stopColor={c2} />
            <stop offset="100%" stopColor={c3} />
          </radialGradient>
          <filter id={id + "n"}>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="3" />
            <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.05 0" />
          </filter>
        </defs>
        <rect width="100%" height="100%" fill={`url(#${id}g)`} />
        {kind === "portrait" && (
          <g opacity="0.5">
            <ellipse cx="200" cy="220" rx="95" ry="120" fill={c1} opacity="0.5" />
            <ellipse cx="200" cy="200" rx="60" ry="78" fill={c1} opacity="0.55" />
            <path d={`M 105 380 Q 200 320 295 380 L 295 540 L 105 540 Z`} fill={c1} opacity="0.4" />
          </g>
        )}
        {kind === "detail" && (
          <g opacity="0.5">
            <circle cx="200" cy="266" r="120" fill={c1} opacity="0.45" />
            <circle cx="200" cy="266" r="70" fill={c1} opacity="0.55" />
          </g>
        )}
        {kind === "hands" && (
          <g opacity="0.45">
            <path d="M 80 280 Q 150 200 220 240 Q 300 280 340 360 L 340 540 L 60 540 Z" fill={c1} opacity="0.45" />
          </g>
        )}
        <rect width="100%" height="100%" fill={`url(#${id}n)`} />
      </svg>
      {label && (
        <div style={{
          position: "absolute", left: 14, bottom: 12,
          padding: "6px 10px",
          background: "rgba(255,255,255,0.85)",
          backdropFilter: "blur(6px)",
          color: "#1A1A1A",
          fontSize: 10,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          fontFamily: "Montserrat, sans-serif",
          fontWeight: 500,
          borderRadius: 1,
        }}>{label}</div>
      )}
    </div>
  );
};

// ============== ICONS — thin, geometric ==============
const Icon = ({ name, size = 22, color = "currentColor" }) => {
  const props = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: color, strokeWidth: 1.3, strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "leaf":    return <svg {...props}><path d="M5 19c0-7 5-12 14-13-1 9-6 14-13 14-1 0-1 0-1-1z"/><path d="M5 19l9-9"/></svg>;
    case "sparkle": return <svg {...props}><path d="M12 3v6M12 15v6M3 12h6M15 12h6"/><path d="M7 7l3 3M14 14l3 3M17 7l-3 3M10 14l-3 3"/></svg>;
    case "shield":  return <svg {...props}><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/></svg>;
    case "clock":   return <svg {...props}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
    case "heart":   return <svg {...props}><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/></svg>;
    case "drop":    return <svg {...props}><path d="M12 3s6 6 6 11a6 6 0 0 1-12 0c0-5 6-11 6-11z"/></svg>;
    case "wa":      return <svg {...props}><path d="M3 21l1.6-4.4A8 8 0 1 1 8 19.5L3 21z"/><path d="M9 9c0 3 3 6 6 6 0 0 1.5 0 2-1l-2-1c-.5.5-1 .5-1.5 0L11 11c-.5-.5-.5-1 0-1.5l-1-2c-1 .5-1 2-1 1.5z" fill={color} stroke="none"/></svg>;
    case "arrow":   return <svg {...props}><path d="M5 12h14M13 6l6 6-6 6"/></svg>;
    case "star":    return <svg {...props} fill={color}><path d="M12 3l2.6 5.5L20 9.4l-4 4 1 5.6L12 16.6 7 19l1-5.6-4-4 5.4-.9L12 3z"/></svg>;
    case "menu":    return <svg {...props}><path d="M4 7h16M4 12h16M4 17h16"/></svg>;
    default: return null;
  }
};

Object.assign(window, { Logo, Placeholder, Icon });
