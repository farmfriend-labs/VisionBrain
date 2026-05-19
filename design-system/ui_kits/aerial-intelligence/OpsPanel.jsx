/* global React, Eyebrow, PanelHeader, Button */
const { useEffect, useRef } = React;

function LogLine({ time, severity, msg }) {
  const colors = {
    i: "var(--ink-3)",       // info dim
    h: "var(--ink-2)",       // header
    s: "var(--accent)",      // success/highlight
    w: "var(--warn)",
    e: "var(--err)",
    a: "var(--ok)",          // amber-ok (mission done)
  };
  return (
    <div style={{
      padding: "0 14px",
      fontFamily: "var(--font-mono)",
      fontSize: 10.5,
      lineHeight: 1.75,
      color: colors[severity] || "var(--ink-3)",
      wordBreak: "break-word",
    }}>
      <span style={{ color: "var(--ink-5)", marginRight: 10 }}>{time}</span>
      {severity === "s" && <span style={{ color: "var(--accent)" }}>▌ </span>}
      {severity === "w" && <span style={{ color: "var(--warn)" }}>! </span>}
      {msg}
    </div>
  );
}

function OperationsLog({ lines }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [lines.length]);
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      <PanelHeader right={<span style={{ fontFamily: "var(--font-mono)", fontSize: 8.5, color: "var(--ink-4)", letterSpacing: ".18em", textTransform: "uppercase", fontWeight: 600 }}>sse · live</span>}>operations log</PanelHeader>
      <div ref={ref} style={{
        flex: 1,
        overflowY: "auto",
        padding: "8px 0",
        minHeight: 0,
      }}>
        {lines.map((l, i) => <LogLine key={i} {...l} />)}
      </div>
    </div>
  );
}

function DetectionCards({ objects, detections, frames }) {
  return (
    <div style={{ borderTop: "1px solid var(--rule)", flexShrink: 0 }}>
      <PanelHeader>detection summary</PanelHeader>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "10px 12px", gap: 6 }}>
        {[
          { v: objects, l: "objects" },
          { v: detections, l: "detections" },
          { v: frames, l: "active frames" },
        ].map((d, i) => (
          <div key={i} style={{
            background: "var(--surface-3)",
            border: "1px solid var(--rule)",
            borderRadius: 2,
            padding: "9px 10px",
            textAlign: "center",
          }}>
            <div style={{
              fontFamily: "var(--font-mono)",
              fontSize: 18,
              fontWeight: 500,
              color: "var(--accent)",
              fontVariantNumeric: "tabular-nums",
              letterSpacing: "-0.01em",
            }}>{d.v}</div>
            <div style={{
              fontSize: 8,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "var(--ink-4)",
              marginTop: 2,
              fontWeight: 600,
            }}>{d.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function FieldReport({ visible }) {
  if (!visible) return null;
  return (
    <div style={{
      flexShrink: 0,
      borderTop: "1px solid var(--rule)",
      display: "flex",
      flexDirection: "column",
      maxHeight: "48%",
    }}>
      <PanelHeader right={
        <div style={{ display: "flex", gap: 6 }}>
          <Button variant="xs">⎘ copy</Button>
          <Button variant="xs">↓ save</Button>
          <Button variant="xs">⛶ expand</Button>
        </div>
      }>field report</PanelHeader>
      <div style={{
        background: "var(--paper)",
        color: "var(--paper-ink)",
        padding: "16px 20px",
        overflowY: "auto",
        fontFamily: "var(--font-serif)",
      }}>
        <div style={{
          fontFamily: "var(--font-mono)",
          fontSize: 8.5,
          fontWeight: 600,
          letterSpacing: "0.22em",
          textTransform: "uppercase",
          color: "#6a6755",
          marginBottom: 6,
        }}>field report · pasture 4 · 14:32</div>
        <div style={{
          fontFamily: "var(--font-serif)",
          fontSize: 18,
          fontWeight: 500,
          fontStyle: "italic",
          lineHeight: 1.2,
          letterSpacing: "-0.01em",
          marginBottom: 12,
        }}>One animal drifting from the herd at 14:32 &mdash; investigate.</div>
        <div style={{
          fontFamily: "var(--font-serif)",
          fontSize: 13,
          lineHeight: 1.65,
        }}>
          Twelve cattle were tracked across 240 frames. Eleven held a tight
          grazing pattern in the south quarter; one — track
          {" "}<span style={{ fontFamily: "var(--font-mono)", fontSize: 12, background: "#ebe5d4", padding: "0 4px" }}>id-07</span>{" "}
          — drifted 80 m north between 14:28 and 14:32 and stopped near the
          fence line. No other animals followed. No predator signatures
          detected on key frames.
        </div>
        <div style={{
          fontFamily: "var(--font-serif)",
          fontSize: 13,
          lineHeight: 1.65,
          marginTop: 10,
        }}>
          <strong style={{ color: "#7a5b2a", fontWeight: 600 }}>Recommend:</strong> walk the
          north fence at first light; verify the gate; check id-07 for
          lameness or calving signs.
        </div>
        <div style={{
          fontFamily: "var(--font-mono)",
          fontSize: 9,
          color: "#7a7666",
          letterSpacing: "0.04em",
          marginTop: 14,
        }}>generated by gemma 4 26b · 287 tokens · 6.4 s · 28.1 tok/s</div>
      </div>
    </div>
  );
}

function OpsPanel({ logLines, completed, hudData }) {
  return (
    <aside style={{
      display: "flex",
      flexDirection: "column",
      background: "var(--surface-2)",
      borderLeft: "1px solid var(--rule)",
      overflow: "hidden",
      width: 372,
      flexShrink: 0,
    }}>
      <OperationsLog lines={logLines} />
      {completed && <DetectionCards objects={hudData.objects} detections={hudData.detections} frames={hudData.frames} />}
      <FieldReport visible={completed} />
    </aside>
  );
}

window.OpsPanel = OpsPanel;
