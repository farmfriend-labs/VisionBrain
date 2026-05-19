/* global React, Logo, Eyebrow, Dot */
const { useState: useState_h } = React;

function HeaderBar({ tab, setTab, modelsReady }) {
  const tabs = ["analyze", "detect", "segment", "track", "sam-3", "ocr"];
  return (
    <header style={{
      height: 52,
      background: "rgba(14,16,13,.94)",
      borderBottom: "1px solid var(--rule)",
      display: "flex",
      alignItems: "center",
      padding: "0 18px",
      gap: 0,
      flexShrink: 0,
      backdropFilter: "blur(8px)",
      WebkitBackdropFilter: "blur(8px)",
      position: "relative",
      zIndex: 2,
    }}>
      {/* lockup */}
      <div style={{ display: "flex", alignItems: "center", gap: 11, marginRight: 32 }}>
        <Logo size={24} />
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <span style={{
            fontFamily: "var(--font-mono)",
            fontSize: 13,
            fontWeight: 600,
            letterSpacing: "0.14em",
            color: "var(--ink-1)",
          }}>farmfriend</span>
          <span style={{
            fontFamily: "var(--font-mono)",
            fontSize: 8.5,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--ink-4)",
          }}>aerial · gcs</span>
        </div>
      </div>

      {/* tabs */}
      <nav style={{ display: "flex", gap: 0, flex: 1 }}>
        {tabs.map(t => {
          const active = t === tab;
          return (
            <button key={t} onClick={() => setTab(t)} style={{
              fontFamily: "var(--font-mono)",
              fontSize: 10,
              fontWeight: active ? 600 : 500,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              padding: "6px 16px",
              background: "none",
              border: "none",
              color: active ? "var(--accent)" : "var(--ink-3)",
              cursor: "pointer",
              position: "relative",
              transition: "color 120ms cubic-bezier(.2,0,0,1)",
            }}>
              {t}
              {active && (
                <span style={{
                  position: "absolute",
                  bottom: -1,
                  left: 16,
                  right: 16,
                  height: 1.5,
                  background: "var(--accent)",
                }} />
              )}
            </button>
          );
        })}
      </nav>

      {/* connection status */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        paddingLeft: 18,
        borderLeft: "1px solid var(--rule)",
      }}>
        <Dot status={modelsReady ? "ok" : "warn"} pulse={modelsReady} />
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 9,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          color: "var(--ink-3)",
        }}>{modelsReady ? "all models ready" : "partial ready"}</span>
      </div>
    </header>
  );
}

window.HeaderBar = HeaderBar;
