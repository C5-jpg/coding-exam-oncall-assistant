const icons = ['⌘', '⌥', '{}', '↵', '✦', '▣', '⌁', '✓', '⌂', '⌬', '⌕', '▱', '↻', '＋', '</>'];

export function AgentFirst() {
  return (
    <section className="agent-first section-pad">
      <div className="section-heading centered">
        <div className="eyebrow">Agent-first</div>
        <h2>Built around tasks, artifacts, and feedback</h2>
        <p>Icon constellations and sparse motion recreate the source page's developer workflow atmosphere.</p>
      </div>
      <ul className="icon-cloud" aria-label="Developer workflow symbols">
        {icons.map((icon, index) => (
          <li key={`${icon}-${index}`}>{icon}</li>
        ))}
      </ul>
    </section>
  );
}
