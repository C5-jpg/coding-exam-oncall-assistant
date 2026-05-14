import { useEffect, useState } from 'react';

export function CookieBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(window.localStorage.getItem('antigravity-demo-cookie') !== 'dismissed');
  }, []);

  if (!visible) return null;

  const dismiss = () => {
    window.localStorage.setItem('antigravity-demo-cookie', 'dismissed');
    setVisible(false);
  };

  return (
    <aside className="cookie-banner" aria-label="Demo notice">
      <p>
        Demo only / Unofficial clone. This local recreation is for UI study and does not provide official Google
        downloads or services.
      </p>
      <button className="primary-cta" type="button" onClick={dismiss}>
        Accept demo notice
      </button>
      <button className="secondary-cta" type="button" onClick={dismiss}>
        Dismiss
      </button>
    </aside>
  );
}
