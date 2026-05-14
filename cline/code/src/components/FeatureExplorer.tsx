import { useState } from 'react';
import { featureTabs } from '../data/sections';

export function FeatureExplorer() {
  const [active, setActive] = useState(0);
  const feature = featureTabs[active];

  return (
    <section className="feature-section section-pad" id="resources">
      <div className="feature-grid">
        <div className="feature-copy">
          <div className="eyebrow">Explore the product</div>
          <h2>{feature.title}</h2>
          <p>{feature.body}</p>
          <div className="feature-tabs" role="tablist" aria-label="Feature explorer">
            {featureTabs.map((tab, index) => (
              <button
                key={tab.title}
                className={index === active ? 'is-active interactive' : 'interactive'}
                type="button"
                onClick={() => setActive(index)}
              >
                {tab.title}
              </button>
            ))}
          </div>
        </div>
        <div className="feature-media interactive">
          <video key={feature.video} src={feature.video} muted autoPlay loop playsInline preload="metadata" />
        </div>
      </div>
    </section>
  );
}
