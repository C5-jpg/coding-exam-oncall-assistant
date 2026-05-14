import { CanvasLayer } from '../particles/CanvasLayer';

export function Pricing() {
  return (
    <section className="pricing-section section-pad" id="pricing">
      <div className="section-heading centered">
        <div className="eyebrow">Pricing</div>
        <h2>Available at no charge while this demo stays local</h2>
      </div>
      <div className="pricing-grid">
        <article className="price-card interactive">
          <CanvasLayer mode="card" className="card-canvas" />
          <div className="price-content">
            <span>For developers</span>
            <h3>Achieve new heights</h3>
            <p>Prototype the agent-first workflow in a local, unofficial interface recreation.</p>
            <a className="primary-cta" href="#download">
              Download
            </a>
          </div>
        </article>
        <article className="price-card muted interactive">
          <CanvasLayer mode="card" className="card-canvas" />
          <div className="price-content">
            <span>Coming soon</span>
            <h3>For organizations</h3>
            <p>Team-level controls are represented as visual placeholders in this learning clone.</p>
            <a className="secondary-cta" href="#">
              Notify me
            </a>
          </div>
        </article>
      </div>
    </section>
  );
}
