import { Navbar } from '../components/Navbar'
import { Hero } from '../components/Hero'
import { BentoFeatures } from '../components/BentoFeatures'
import { KpiCounters } from '../components/KpiCounters'
import { FincasMap } from '../components/FincasMap'
import { Faq } from '../components/Faq'
import { CtaFinal } from '../components/CtaFinal'
import { Footer } from '../components/Footer'

export function Landing() {
  return (
    <>
      <div className="noise-overlay" />
      <Navbar />
      <main>
        <Hero />
        <KpiCounters />
        <BentoFeatures />
        <FincasMap />
        <Faq />
        <CtaFinal />
      </main>
      <Footer />
    </>
  )
}
