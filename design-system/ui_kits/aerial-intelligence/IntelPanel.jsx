/* global React, Eyebrow, Dot, StatusPill, PanelHeader, Button */

function ModelCard({ name, id, size, badge, status, note }) {
  return (
    <div style={{
      padding: "12px 14px",
      borderBottom: "1px solid var(--rule)",
      transition: "background 120ms cubic-bezier(.2,0,0,1)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
        <Dot status={status} pulse={status === "ok"} />
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11.5,
          fontWeight: 600,
          color: "var(--ink-1)",
          flex: 1,
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}>{name}</span>
        <StatusPill status={status}>{badge}</StatusPill>
      </div>
      <div style={{
        fontFamily: "var(--font-mono)",
        fontSize: 9.5,
        color: "var(--ink-3)",
        marginBottom: 6,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
      }}>{id}</div>
      <div style={{ display: "flex", gap: 10, alignItems: "baseline" }}>
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10,
          color: "var(--ink-2)",
          fontVariantNumeric: "tabular-nums",
        }}>{size}</span>
        <span style={{ fontSize: 9, color: "var(--ink-4)" }}>·</span>
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 9.5,
          color: "var(--ink-3)",
        }}>{note}</span>
      </div>
    </div>
  );
}

function StatCell({ label, value, accent, last, rightOpen }) {
  return (
    <div style={{
      padding: "10px 14px",
      borderBottom: last ? "none" : "1px solid var(--rule)",
      borderRight: rightOpen ? "none" : "1px solid var(--rule)",
    }}>
      <div style={{
        fontFamily: "var(--font-mono)",
        fontSize: 8.5,
        fontWeight: 600,
        letterSpacing: "0.16em",
        textTransform: "uppercase",
        color: "var(--ink-4)",
        marginBottom: 4,
      }}>{label}</div>
      <div style={{
        fontFamily: "var(--font-mono)",
        fontSize: value === "—" ? 13 : 18,
        fontWeight: 500,
        color: accent ? "var(--accent)" : (value === "—" ? "var(--ink-4)" : "var(--ink-1)"),
        fontVariantNumeric: "tabular-nums",
        letterSpacing: "-0.01em",
      }}>{value}</div>
    </div>
  );
}

function IntelPanel({ models, gemmaRemote, mission }) {
  return (
    <aside style={{
      background: "var(--surface-2)",
      borderRight: "1px solid var(--rule)",
      overflowY: "auto",
      overflowX: "hidden",
      width: 248,
      flexShrink: 0,
    }}>
      <PanelHeader>model intel</PanelHeader>
      {models.map(m => <ModelCard key={m.id} {...m} />)}

      <PanelHeader>remote server</PanelHeader>
      <div style={{
        padding: "8px 14px",
        borderBottom: "1px solid var(--rule)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <span style={{ fontSize: 9, color: "var(--ink-4)", letterSpacing: ".08em", textTransform: "uppercase", fontWeight: 600 }}>endpoint</span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, color: "var(--ink-2)" }}>100.72.41.118:8080</span>
      </div>
      <div style={{
        padding: "8px 14px",
        borderBottom: "1px solid var(--rule)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <span style={{ fontSize: 9, color: "var(--ink-4)", letterSpacing: ".08em", textTransform: "uppercase", fontWeight: 600 }}>gemma</span>
        <span style={{
          fontFamily: "var(--font-mono)",
          fontSize: 9.5,
          color: gemmaRemote ? "var(--ok)" : "var(--err)",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}>
          <Dot status={gemmaRemote ? "ok" : "err"} size={6} />
          {gemmaRemote ? "online" : "offline"}
        </span>
      </div>

      <PanelHeader>last mission</PanelHeader>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
        <StatCell label="frames"     value={mission.frames}     accent={mission.frames !== "—"} />
        <StatCell label="objects"    value={mission.objects}    accent={mission.objects !== "—"} rightOpen />
        <StatCell label="detections" value={mission.detections} accent={false} last />
        <StatCell label="duration"   value={mission.duration}   accent={false} last rightOpen />
      </div>

      <PanelHeader>quick actions</PanelHeader>
      <div style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
        <Button variant="xs" style={{ width: "100%", textAlign: "left", justifyContent: "flex-start", display: "flex" }}>↻ refresh status</Button>
        <Button variant="xs" style={{ width: "100%", textAlign: "left", justifyContent: "flex-start", display: "flex" }}>⌫ clear log</Button>
        <Button variant="xs" state={mission.frames === "—" ? "disabled" : "default"} style={{ width: "100%", textAlign: "left", justifyContent: "flex-start", display: "flex" }}>↓ download video</Button>
        <Button variant="xs" state={mission.frames === "—" ? "disabled" : "default"} style={{ width: "100%", textAlign: "left", justifyContent: "flex-start", display: "flex" }}>↓ download report</Button>
      </div>
    </aside>
  );
}

window.IntelPanel = IntelPanel;
