import { CanvasLayer } from '../particles/CanvasLayer';

export function DownloadSection() {
  return (
    <section className="download-section section-pad" id="download">
      <div className="download-panel">
        <CanvasLayer mode="download" className="download-canvas" />
        <div className="download-content">
          <div className="eyebrow">Download</div>
          <h2>Experience liftoff on Windows</h2>
          <p>
            Demo only / Unofficial clone. These buttons intentionally do not download official Google software.
          </p>
          <div className="button-row">
            <a className="primary-cta interactive" href="#">
              Download for x64
            </a>
            <a className="secondary-cta interactive" href="#">
              Download for ARM64
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
