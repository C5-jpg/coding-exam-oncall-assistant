import { AgentFirst } from './components/AgentFirst';
import { BlogGrid } from './components/BlogGrid';
import { CookieBanner } from './components/CookieBanner';
import { DownloadSection } from './components/DownloadSection';
import { FeatureExplorer } from './components/FeatureExplorer';
import { Footer } from './components/Footer';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { Pricing } from './components/Pricing';
import { ProductSection } from './components/ProductSection';
import { UseCases } from './components/UseCases';
import { VideoSection } from './components/VideoSection';

export default function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <VideoSection />
        <AgentFirst />
        <ProductSection />
        <FeatureExplorer />
        <UseCases />
        <Pricing />
        <BlogGrid />
        <DownloadSection />
      </main>
      <Footer />
      <CookieBanner />
      <div style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        background: '#fff3cd',
        color: '#856404',
        textAlign: 'center',
        padding: '6px 16px',
        fontSize: '12px',
        fontFamily: 'system-ui, sans-serif',
      }}>
        ⚠️ Demo only — Unofficial clone for local learning. Not affiliated with Google.
      </div>
    </>
  );
}
