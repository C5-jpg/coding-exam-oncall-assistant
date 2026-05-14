import { useCases } from '../data/sections';

export function UseCases() {
  return (
    <section className="use-cases section-pad" id="use-cases">
      <div className="section-heading">
        <div className="eyebrow">Use cases</div>
        <h2>Built for developers for the agent-first era</h2>
      </div>
      <div className="case-grid">
        {useCases.map((item) => (
          <article className="case-card interactive" key={item.title}>
            <img src={item.image} alt="" />
            <div>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </div>
          </article>
        ))}
      </div>
      <div className="slider-controls" aria-hidden="true">
        <button type="button">←</button>
        <button type="button">→</button>
      </div>
    </section>
  );
}
