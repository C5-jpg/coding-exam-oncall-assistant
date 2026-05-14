import { blogs } from '../data/sections';

export function BlogGrid() {
  return (
    <section className="blog-section section-pad" id="blog">
      <div className="section-heading split">
        <div>
          <div className="eyebrow">Latest blogs</div>
          <h2>Updates from the agent-first workflow</h2>
        </div>
        <a className="secondary-cta interactive" href="#">
          View blog
        </a>
      </div>
      <div className="blog-grid">
        {blogs.map((item) => (
          <article className="blog-card interactive" key={item.title}>
            <img src={item.image} alt="" />
            <span>{item.date}</span>
            <h3>{item.title}</h3>
          </article>
        ))}
      </div>
    </section>
  );
}
