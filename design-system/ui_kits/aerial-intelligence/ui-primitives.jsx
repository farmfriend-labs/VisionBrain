/* global React */
const { useState, useEffect, useRef } = React;

// ─── FarmFriend brand mark ──────────────────────────────────────
// Two-tone teal + green by default. Pass `mono` (a color / CSS var)
// to render single-color, or override --ff-teal / --ff-green on a
// parent to retheme. Square 1:1 viewBox.
function Logo({ size = 22, mono = null, style }) {
  const teal  = mono || "var(--ff-teal, #42A4AC)";
  const green = mono || "var(--ff-green, #42B67E)";
  return (
    <svg width={size} height={size} viewBox="0 0 250 250"
         style={{ display: "block", flexShrink: 0, ...style }}
         aria-label="FarmFriend" role="img">
      <g fill={teal}>
        <path d="m120.1 42.92v3.78c0 0.56-0.45 1.02-1.01 1.02h-55.54c-0.69 0-1.24 0.55-1.24 1.24v142c0 0.63-0.31 0.94-0.93 0.94h-3.15c-0.63 0-0.8-0.43-0.8-1.05v-147.6c0-0.62 0.32-1.05 0.94-1.05h60.83c0.56 0 0.9 0.22 0.9 0.66z"/>
        <path d="m119.9 53.22v4.99c0 0.56-0.34 0.85-0.9 0.85h-43.59c-0.69 0-1.13 0.5-1.13 1.19v130.5c0 0.63-0.17 1.12-0.79 1.12h-4.88c-0.57 0-0.91-0.49-0.91-1.12v-136.8c0-0.63 0.44-1.18 1.06-1.18h50.24c0.56 0 0.9 0.01 0.9 0.46z"/>
        <path d="m119.8 65.41v3.15c0 0.62-0.55 0.93-1.17 0.93h-31.76c-0.62 0-1.07 0.55-1.07 1.18v38.2c0 0.62 0.32 1.06 0.94 1.06h29.43c0.62 0 0.95 0.38 0.95 1v3.31c0 0.62-0.5 0.94-1.13 0.94h-34.01c-0.62 0-1.06-0.32-1.06-0.94v-48.33c0-0.63 0.44-1.18 1.06-1.18h36.87c0.62 0 0.95 0.06 0.95 0.68z"/>
        <path d="m117.4 121.1v4.71c0 0.62-0.55 0.99-1.17 0.99h-34.12c-0.62 0-1.17-0.49-1.17-1.11v-4.02c0-0.63 0.55-1.3 1.17-1.3h34.34c0.62 0 0.95 0.18 0.95 0.73z"/>
        <path d="m117 132.7v3.59c0 0.63-0.55 1.12-1.17 1.12h-28.49c-0.62 0-1.3 0.55-1.3 1.17v51.8c0 0.62-0.27 1.32-0.89 1.32h-3.22c-0.62 0-1-0.55-1-1.17v-56.94c0-0.62 0.55-1.3 1.17-1.3h34c0.62 0 0.9-0.15 0.9 0.41z"/>
      </g>
      <g fill={green}>
        <path d="m183.4 67.61h-62.43c-0.63 0-0.95 0.55-0.95 1.17v148.3c0 0.62 0.32 0.89 0.95 0.89h3.89v-143.6c0-0.69 0.55-1.14 1.24-1.14h56.67c0.63 0 0.86-0.44 0.86-1.06v-3.84c0-0.44 0.31-0.7-0.23-0.7z"/>
        <path d="m183.2 79.41h-51c-0.63 0-1.28 0.22-1.28 0.84v137.6h5.83v-131.5c0-0.69 0.32-1.13 0.94-1.13h45.03c0.62 0 0.8-0.39 0.8-1.01v-4.16c0-0.56 0.24-0.71-0.32-0.71z"/>
        <path d="m183.2 90.75h-38.47c-0.63 0-1.18 0.67-1.18 1.29v48.08c0 0.62 0.27 0.83 0.89 0.83h35.28c0.62 0 0.72-0.33 0.72-0.95v-3.26c0-0.62-0.38-1-1-1h-29.76c-0.62 0-0.94-0.32-0.94-0.94v-37.79c0-0.63 0.44-1.35 1.06-1.35h33.46c0.56 0 0.46-0.21 0.46-0.77v-3.15c0-0.62 0.04-0.99-0.52-0.99z"/>
        <path d="m180.2 146.7h-35.45c-0.63 0-1.23 0.44-1.23 1.06v4.33c0 0.62 0.6 1.06 1.23 1.06h34.79c0.62 0 0.97-0.44 0.97-1.06v-4.66c0-0.56 0.24-0.73-0.31-0.73z"/>
        <path d="m179.7 159h-34.89c-0.63 0-1.33 0.32-1.33 0.94v57.99h4.88c0.32 0 0.32-0.31 0.32-0.93v-51.3c0-0.62 0.44-1.34 1.06-1.34h29.96c0.62 0 0.57-0.44 0.57-1.06v-3.48c0-0.56-0.01-0.82-0.57-0.82z"/>
      </g>
    </svg>
  );
}

// ─── Eyebrow label (small caps, wide tracking) ───────────────────
function Eyebrow({ children, color, style }) {
  return (
    <div style={{
      fontFamily: "var(--font-mono)",
      fontSize: 9,
      fontWeight: 600,
      letterSpacing: "0.22em",
      textTransform: "uppercase",
      color: color || "var(--ink-3)",
      ...style,
    }}>{children}</div>
  );
}

// ─── Status dot ──────────────────────────────────────────────────
function Dot({ status = "ok", pulse = false, size = 7 }) {
  const color = {
    ok: "var(--ok)",
    warn: "var(--warn)",
    err: "var(--err)",
    info: "var(--info)",
    idle: "var(--ink-4)",
  }[status];
  return (
    <span style={{
      width: size, height: size, borderRadius: "50%",
      background: color, flexShrink: 0,
      animation: pulse ? "ai-pulse 2.5s ease-in-out infinite" : undefined,
    }} />
  );
}

// ─── Status pill (chip with dot + label) ─────────────────────────
function StatusPill({ status = "ok", children }) {
  const c = {
    ok:   { fg: "var(--ok)",   bg: "rgba(143,169,122,.07)", bd: "rgba(143,169,122,.4)" },
    warn: { fg: "var(--warn)", bg: "rgba(200,151,102,.07)", bd: "rgba(200,151,102,.4)" },
    err:  { fg: "var(--err)",  bg: "rgba(182,97,80,.07)",   bd: "rgba(182,97,80,.4)" },
    idle: { fg: "var(--ink-3)", bg: "transparent",          bd: "var(--rule-strong)" },
  }[status];
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "2px 7px",
      border: `1px solid ${c.bd}`,
      background: c.bg,
      borderRadius: 2,
      fontFamily: "var(--font-mono)",
      fontSize: 8,
      fontWeight: 600,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: c.fg,
    }}>{children}</span>
  );
}

// ─── Button ──────────────────────────────────────────────────────
function Button({ variant = "secondary", state = "default", children, onClick, style, ...rest }) {
  const base = {
    fontFamily: "var(--font-mono)",
    cursor: state === "disabled" ? "not-allowed" : "pointer",
    border: "1px solid var(--rule-strong)",
    borderRadius: 2,
    background: "transparent",
    color: "var(--ink-2)",
    transition: "all 120ms cubic-bezier(.2,0,0,1)",
    fontWeight: 500,
    letterSpacing: "0.12em",
    textTransform: "lowercase",
    height: 30,
    padding: "0 14px",
    fontSize: 11,
  };
  const variants = {
    launch: {
      ...base,
      height: 34,
      padding: "0 18px",
      fontWeight: 600,
      fontSize: 11,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      border: "1px solid var(--accent)",
      color: "var(--accent)",
      background: "rgba(212,181,114,.06)",
    },
    running: {
      ...base,
      height: 34,
      padding: "0 18px",
      fontWeight: 600,
      fontSize: 11,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      border: "1px solid var(--warn)",
      color: "var(--warn)",
      background: "rgba(200,151,102,.06)",
      cursor: "wait",
    },
    secondary: { ...base },
    ghost: {
      ...base,
      border: "none",
      color: "var(--ink-3)",
      textDecoration: "underline",
      textUnderlineOffset: 3,
      textDecorationColor: "var(--ink-4)",
    },
    xs: {
      ...base,
      height: 22,
      padding: "0 9px",
      fontSize: 9,
      fontWeight: 600,
      letterSpacing: "0.12em",
      textTransform: "uppercase",
      border: "1px solid var(--rule)",
      color: "var(--ink-3)",
    },
  };
  const disabled = state === "disabled";
  return (
    <button
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      style={{
        ...variants[variant],
        ...(disabled ? { opacity: 0.4, cursor: "not-allowed" } : null),
        ...style,
      }}
      {...rest}
    >{children}</button>
  );
}

// ─── Label (form-style small cap label) ──────────────────────────
function Label({ children }) {
  return (
    <label style={{
      fontFamily: "var(--font-mono)",
      fontSize: 8,
      fontWeight: 600,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: "var(--ink-4)",
    }}>{children}</label>
  );
}

// ─── Panel header (eyebrow + bottom rule) ────────────────────────
function PanelHeader({ children, right }) {
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "9px 14px 7px",
      borderBottom: "1px solid var(--rule)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ width: 12, height: 1, background: "var(--accent)", opacity: 0.5 }} />
        <Eyebrow>{children}</Eyebrow>
      </div>
      {right}
    </div>
  );
}

// expose
Object.assign(window, { Logo, Eyebrow, Dot, StatusPill, Button, Label, PanelHeader });
