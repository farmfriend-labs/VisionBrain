/* global React, Label, Button */
const { useState: useState_cfg } = React;

function Field({ label, children, w }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3, width: w || "auto", flex: w ? "0 0 auto" : 1, minWidth: 0 }}>
      <Label>{label}</Label>
      {children}
    </div>
  );
}

const inputStyle = {
  fontFamily: "var(--font-mono)",
  fontSize: 11,
  background: "var(--surface-3)",
  border: "1px solid var(--rule)",
  color: "var(--ink-1)",
  padding: "3px 8px",
  height: 24,
  borderRadius: 2,
  outline: "none",
  width: "100%",
};

function ConfigBar({ tab, fileLoaded, running, onLaunch }) {
  const [query, setQuery] = useState_cfg("cattle in the pasture");
  const [prompts, setPrompts] = useState_cfg("cow cattle animal");
  const [thresh, setThresh] = useState_cfg(0.15);

  return (
    <div style={{
      height: 60,
      background: "rgba(20,22,18,.96)",
      borderTop: "1px solid var(--rule)",
      display: "flex",
      alignItems: "center",
      padding: "0 16px",
      gap: 12,
      flexShrink: 0,
      backdropFilter: "blur(8px)",
      WebkitBackdropFilter: "blur(8px)",
    }}>
      {tab === "analyze" && (
        <React.Fragment>
          <Field label="query">
            <input value={query} onChange={e => setQuery(e.target.value)} style={inputStyle} />
          </Field>
          <Field label="prompts" w={140}>
            <input value={prompts} onChange={e => setPrompts(e.target.value)} style={inputStyle} />
          </Field>
          <Field label="threshold" w={110}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, height: 24 }}>
              <input type="range" min={0} max={0.5} step={0.01} value={thresh}
                     onChange={e => setThresh(parseFloat(e.target.value))}
                     style={{ flex: 1, accentColor: "var(--accent)", height: 2 }} />
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10,
                color: "var(--accent)", fontVariantNumeric: "tabular-nums",
                minWidth: 28, textAlign: "right",
              }}>{thresh.toFixed(2)}</span>
            </div>
          </Field>
          <Field label="res" w={64}>
            <select style={{ ...inputStyle, appearance: "none" }} defaultValue="1008">
              <option>512</option><option>756</option><option>1008</option>
            </select>
          </Field>
          <Field label="every" w={56}>
            <select style={{ ...inputStyle, appearance: "none" }} defaultValue="2">
              <option>1F</option><option>2F</option><option>3F</option><option>5F</option>
            </select>
          </Field>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--ink-2)", cursor: "pointer" }}>
              <input type="checkbox" defaultChecked style={{ accentColor: "var(--accent)" }} />
              <span>report</span>
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--ink-3)", cursor: "pointer" }}>
              <input type="checkbox" style={{ accentColor: "var(--accent)" }} />
              <span>falcon+</span>
            </label>
          </div>
        </React.Fragment>
      )}
      {tab !== "analyze" && (
        <Field label={tab === "ocr" ? "ocr question" : "expression query"}>
          <input defaultValue={tab === "ocr" ? "read all text in the image" : "cattle"} style={inputStyle} />
        </Field>
      )}

      <div style={{ width: 1, height: 32, background: "var(--rule)" }} />

      <Button
        variant={running ? "running" : "launch"}
        state={!fileLoaded || running ? "disabled" : "default"}
        onClick={onLaunch}
        style={!fileLoaded ? { opacity: 0.4 } : null}
      >
        {running ? "running · 142/240" : "▶ launch"}
      </Button>
    </div>
  );
}

window.ConfigBar = ConfigBar;
