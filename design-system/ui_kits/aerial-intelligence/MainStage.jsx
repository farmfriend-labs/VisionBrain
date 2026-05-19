/* global React, Eyebrow */

function PipelineStage({ name, sub, state }) {
  // state: 'pending' | 'active' | 'done'
  const colors = {
    pending: { border: "var(--rule-strong)", text: "var(--ink-3)", bg: "transparent" },
    active:  { border: "var(--accent)",      text: "var(--accent)", bg: "rgba(212,181,114,.07)" },
    done:    { border: "var(--accent-deep)", text: "var(--accent-deep)", bg: "rgba(212,181,114,.03)" },
  }[state];
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <div style={{
        width: 60,
        height: 60,
        borderRadius: "50%",
        border: `1.5px solid ${colors.border}`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: colors.bg,
        transition: "all 280ms cubic-bezier(.2,0,0,1)",
      }}>
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 8.5,
          fontWeight: 600,
          letterSpacing: "0.12em",
          color: colors.text,
          textTransform: "uppercase",
        }}>{name}</span>
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 7,
          color: colors.text,
          marginTop: 1,
        }}>{sub}</span>
      </div>
    </div>
  );
}

function PipelineLine({ active }) {
  return (
    <div style={{
      flex: "0 1 80px",
      height: 1.5,
      background: active ? "var(--accent-deep)" : "var(--rule-strong)",
      marginBottom: 24,
      margin: "0 6px 24px",
      transition: "background 280ms cubic-bezier(.2,0,0,1)",
    }} />
  );
}

function Pipeline({ stage }) {
  // stage: 0 (idle) → 1 (sam) → 2 (falcon) → 3 (gemma) → 4 (done)
  const s = i => stage > i ? "done" : (stage === i ? "active" : "pending");
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "14px 36px 16px",
      borderTop: "1px solid var(--rule)",
      background: "var(--surface-1)",
      flexShrink: 0,
    }}>
      <PipelineStage name="sam"    sub="3.1"            state={s(1)} />
      <PipelineLine active={stage >= 2} />
      <PipelineStage name="falcon" sub="perception"     state={s(2)} />
      <PipelineLine active={stage >= 3} />
      <PipelineStage name="gemma"  sub="4 · 26b"        state={s(3)} />
    </div>
  );
}

function DropZone({ filled, fileName, onLaunch }) {
  return (
    <div style={{
      flex: 1,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 14,
      border: filled
        ? "1px dashed var(--accent)"
        : "1px dashed var(--rule-strong)",
      margin: 20,
      background: filled ? "rgba(212,181,114,.03)" : "transparent",
      cursor: "pointer",
      transition: "all 180ms cubic-bezier(.2,0,0,1)",
    }}>
      <div style={{
        fontSize: 38,
        color: filled ? "var(--accent)" : "var(--ink-4)",
        lineHeight: 1,
        userSelect: "none",
      }}>⬡</div>
      <div style={{
        fontFamily: "var(--font-mono)",
        fontSize: 10,
        letterSpacing: "0.22em",
        textTransform: "uppercase",
        color: filled ? "var(--ink-1)" : "var(--ink-3)",
      }}>{filled ? "ready to launch" : "drop drone footage"}</div>
      {filled ? (
        <div style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--accent)",
          padding: "3px 12px",
          border: "1px solid var(--accent-deep)",
          background: "rgba(212,181,114,.05)",
          borderRadius: 2,
        }}>⬡  {fileName}</div>
      ) : (
        <div style={{
          fontFamily: "var(--font-mono)",
          fontSize: 9,
          color: "var(--ink-4)",
          letterSpacing: "0.1em",
        }}>mp4 · mov · avi · webm</div>
      )}
    </div>
  );
}

function VideoFrame({ src, hudData }) {
  return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", padding: "16px 20px 8px", gap: 10 }}>
      <div style={{
        flex: 1,
        minHeight: 0,
        position: "relative",
        background: "var(--surface-2)",
        overflow: "hidden",
      }}>
        {/* fake drone still */}
        <div style={{
          position: "absolute", inset: 0,
          background: `
            radial-gradient(ellipse 60% 40% at 32% 60%, rgba(143,169,122,.16), transparent 70%),
            radial-gradient(ellipse 45% 35% at 70% 45%, rgba(200,151,102,.12), transparent 70%),
            radial-gradient(ellipse 30% 50% at 88% 70%, rgba(212,181,114,.08), transparent 70%),
            linear-gradient(180deg, #181b16 0%, #1a1d17 60%, #1f221a 100%)
          `,
        }} />
        {/* faint terrain lines */}
        <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.18 }}>
          <path d="M0 60 Q 200 80, 400 70 T 800 90" stroke="var(--ink-3)" strokeWidth="0.5" fill="none" />
          <path d="M0 130 Q 250 150, 500 140 T 1000 160" stroke="var(--ink-3)" strokeWidth="0.5" fill="none" />
          <path d="M0 210 Q 300 230, 600 220 T 1200 240" stroke="var(--ink-3)" strokeWidth="0.5" fill="none" />
        </svg>

        {/* track boxes */}
        <TrackBox left="14%" top="48%" w={32} h={22} id="07" color="var(--accent)" />
        <TrackBox left="28%" top="60%" w={28} h={20} id="03" color="var(--ok)" />
        <TrackBox left="44%" top="52%" w={34} h={22} id="11" color="var(--ok)" />
        <TrackBox left="58%" top="64%" w={26} h={18} id="04" color="var(--ok)" />
        <TrackBox left="72%" top="50%" w={30} h={20} id="09" color="var(--ok)" />

        {/* corner brackets */}
        <Corner pos="tl" /><Corner pos="tr" /><Corner pos="bl" /><Corner pos="br" />

        {/* HUD label */}
        <div style={{
          position: "absolute", top: 16, left: 28,
          fontFamily: "var(--font-mono)", fontSize: 9, fontWeight: 600,
          letterSpacing: "0.22em", textTransform: "uppercase", color: "var(--accent)",
        }}>live · pasture 4</div>
        <div style={{
          position: "absolute", top: 16, right: 28,
          fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--ink-3)",
          letterSpacing: "0.04em", fontVariantNumeric: "tabular-nums",
        }}>t={hudData.time}  ·  {hudData.frames}</div>
        <div style={{
          position: "absolute", bottom: 16, right: 28,
          fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--ink-3)",
          letterSpacing: "0.04em",
        }}>{hudData.objects} tracks · 0.15 thresh</div>
      </div>

      {/* HUD readout strip */}
      <div style={{ display: "flex", gap: 26, padding: "0 4px" }}>
        <HudReadout label="frames"     value={hudData.frames} />
        <HudReadout label="objects"    value={hudData.objects} />
        <HudReadout label="detections" value={hudData.detections} dim />
        <HudReadout label="fps"        value={hudData.fps} dim />
        <HudReadout label="duration"   value={hudData.duration} dim />
      </div>
    </div>
  );
}

function HudReadout({ label, value, dim }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <span style={{
        fontFamily: "var(--font-mono)", fontSize: 8, letterSpacing: "0.18em",
        textTransform: "uppercase", color: "var(--ink-4)", fontWeight: 600,
      }}>{label}</span>
      <span style={{
        fontFamily: "var(--font-mono)",
        fontSize: dim ? 13 : 16,
        fontWeight: 500,
        color: dim ? "var(--ink-1)" : "var(--accent)",
        fontVariantNumeric: "tabular-nums",
        letterSpacing: "-0.01em",
      }}>{value}</span>
    </div>
  );
}

function TrackBox({ left, top, w, h, id, color }) {
  return (
    <React.Fragment>
      <div style={{
        position: "absolute", left, top,
        width: w, height: h,
        border: `1.5px solid ${color}`,
        background: `${color}10`,
      }} />
      <div style={{
        position: "absolute", left, top: `calc(${top} - 12px)`,
        fontFamily: "var(--font-mono)", fontSize: 8.5,
        color: color, background: "var(--canvas)",
        padding: "0 4px", letterSpacing: "0.08em",
      }}>id-{id}</div>
    </React.Fragment>
  );
}

function Corner({ pos }) {
  const p = {
    tl: { top: 8,    left: 8,   borderTop: "1.5px solid var(--accent)",    borderLeft: "1.5px solid var(--accent)" },
    tr: { top: 8,    right: 8,  borderTop: "1.5px solid var(--accent)",    borderRight: "1.5px solid var(--accent)" },
    bl: { bottom: 8, left: 8,   borderBottom: "1.5px solid var(--accent)", borderLeft: "1.5px solid var(--accent)" },
    br: { bottom: 8, right: 8,  borderBottom: "1.5px solid var(--accent)", borderRight: "1.5px solid var(--accent)" },
  }[pos];
  return <div style={{ position: "absolute", width: 16, height: 16, ...p }} />;
}

function MainStage({ filled, fileName, stage, hudData, completed }) {
  return (
    <main style={{
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
      background: "var(--canvas)",
      flex: 1,
      minWidth: 0,
    }}>
      <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
        {completed
          ? <VideoFrame hudData={hudData} />
          : <DropZone filled={filled} fileName={fileName} />}
      </div>
      <Pipeline stage={stage} />
    </main>
  );
}

window.MainStage = MainStage;
