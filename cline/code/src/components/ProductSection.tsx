import { CanvasLayer } from '../particles/CanvasLayer';

export function ProductSection() {
  return (
    <section className="product-section section-pad" id="product">
      <CanvasLayer mode="product" className="product-canvas" />
      <div className="product-copy">
        <div className="eyebrow">Product</div>
        <h2>Agents that help you achieve liftoff</h2>
        <p>
          A local recreation of the product overview state, including the large dotted ribbon field observed on the
          source page.
        </p>
        <div className="button-row">
          <a className="primary-cta interactive" href="#download">
            Download for x64
          </a>
          <a className="secondary-cta interactive" href="#download">
            Download for ARM64
          </a>
        </div>
      </div>
    </section>
  );
}
