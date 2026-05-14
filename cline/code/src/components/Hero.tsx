import { CanvasLayer } from '../particles/CanvasLayer';

export function Hero() {
  return (
    <section className="hero" id="top">
      <CanvasLayer mode="hero" className="hero-canvas" />
      <div className="hero-inner">
        <div className="hero-brand">
          <img src="/assets/images/antigravity-cursor.png" alt="" />
          <span>Google Antigravity</span>
        </div>
        <h1>Experience liftoff with the next-gen agent platform</h1>
        <div className="hero-actions">
          <a className="primary-cta interactive" href="#download">
            <span aria-hidden="true">⊞</span> Download for Windows
          </a>
          <a className="secondary-cta interactive" href="#use-cases">
            Explore use cases
          </a>
        </div>
      </div>
    </section>
  );
}
