export function VideoSection() {
  return (
    <section className="video-section section-pad">
      <div className="video-card interactive">
        <video src="/assets/videos/welcome-antigravity.mp4" muted loop playsInline preload="metadata" poster="" />
        <div className="video-overlay">
          <span aria-hidden="true">▶</span>
          <span>Play intro</span>
        </div>
      </div>
    </section>
  );
}
