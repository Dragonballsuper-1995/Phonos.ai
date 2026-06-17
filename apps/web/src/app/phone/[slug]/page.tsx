import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { formatPrice } from '@/lib/utils';
import styles from './phone.module.css';

// Mock fetching function
async function getPhoneData(slug: string) {
  // Simulate API fetch
  return {
    id: 'p1',
    fullName: 'Samsung Galaxy S24 Ultra',
    brand: 'Samsung',
    slug: 'samsung-galaxy-s24-ultra',
    price: 129999,
    imageUrl: 'https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-ultra-5g-sm-s928-u.jpg',
    description: 'The ultimate Android flagship with a built-in S Pen, titanium frame, and revolutionary Galaxy AI features.',
    scores: {
      performance: 98,
      camera: 95,
      battery: 92,
      display: 99,
      value: 75
    },
    specs: {
      display: '6.8" Dynamic LTPO AMOLED 2X, 120Hz, HDR10+, 2600 nits',
      processor: 'Snapdragon 8 Gen 3 for Galaxy',
      ram: '12GB LPDDR5X',
      storage: '256GB / 512GB / 1TB UFS 4.0',
      camera: '200MP Main + 50MP Periscope + 10MP Telephoto + 12MP Ultrawide',
      frontCamera: '12MP',
      battery: '5000 mAh, 45W Wired, 15W Wireless',
      os: 'Android 14, One UI 6.1'
    },
    pros: ['Incredible anti-reflective display', '7 years of updates', 'Excellent battery life', 'Versatile camera system'],
    cons: ['Very expensive', 'Heavy and bulky', 'Slow 45W charging compared to rivals']
  };
}

export default async function PhonePage({ params }: { params: { slug: string } }) {
  const phone = await getPhoneData(params.slug);

  return (
    <div className={styles.container}>
      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>
        <Link href="/">Home</Link> &gt; <Link href="/results">Phones</Link> &gt; <span>{phone.fullName}</span>
      </div>

      <div className={styles.hero}>
        <div className={styles.imageGallery}>
          <div className={styles.mainImage}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={phone.imageUrl} alt={phone.fullName} />
          </div>
        </div>

        <div className={styles.heroContent}>
          <div className={styles.brandBadge}>{phone.brand}</div>
          <h1 className={styles.title}>{phone.fullName}</h1>
          <div className={styles.price}>{formatPrice(phone.price)}</div>
          <p className={styles.description}>{phone.description}</p>
          
          <div className={styles.actions}>
            <Button size="lg" className={styles.buyBtn}>Buy Now</Button>
            <Link href={`/compare?p1=${phone.slug}`} passHref>
              <Button variant="outline" size="lg">Compare</Button>
            </Link>
          </div>
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.mainCol}>
          <Card className={styles.section}>
            <h2>Detailed Specifications</h2>
            <div className={styles.specsTable}>
              {Object.entries(phone.specs).map(([key, value]) => (
                <div key={key} className={styles.specRow}>
                  <div className={styles.specLabel}>
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </div>
                  <div className={styles.specValue}>{value}</div>
                </div>
              ))}
            </div>
          </Card>

          <div className={styles.prosCons}>
            <Card className={styles.prosCard}>
              <h3 className={styles.prosTitle}>👍 Pros</h3>
              <ul className={styles.list}>
                {phone.pros.map((pro, i) => <li key={i}>{pro}</li>)}
              </ul>
            </Card>
            <Card className={styles.consCard}>
              <h3 className={styles.consTitle}>👎 Cons</h3>
              <ul className={styles.list}>
                {phone.cons.map((con, i) => <li key={i}>{con}</li>)}
              </ul>
            </Card>
          </div>
        </div>

        <div className={styles.sideCol}>
          <Card className={styles.section}>
            <h2>Fone.ai Scores</h2>
            <div className={styles.scoresList}>
              <ScoreBar label="Performance" score={phone.scores.performance} />
              <ScoreBar label="Camera" score={phone.scores.camera} />
              <ScoreBar label="Display" score={phone.scores.display} />
              <ScoreBar label="Battery" score={phone.scores.battery} />
              <ScoreBar label="Value" score={phone.scores.value} />
            </div>
          </Card>

          <Card className={styles.section}>
            <h2>Review Sentiment</h2>
            <div className={styles.sentimentViz}>
              <div className={styles.sentimentBar}>
                <div className={styles.positive} style={{ width: '85%' }}>85%</div>
                <div className={styles.neutral} style={{ width: '10%' }}></div>
                <div className={styles.negative} style={{ width: '5%' }}></div>
              </div>
              <div className={styles.sentimentLegend}>
                <span><span className={styles.dot} style={{ background: '#10b981' }}></span> Positive</span>
                <span><span className={styles.dot} style={{ background: '#94a3b8' }}></span> Neutral</span>
                <span><span className={styles.dot} style={{ background: '#ef4444' }}></span> Negative</span>
              </div>
            </div>
            <p className={styles.sentimentText}>Based on analysis of 124 professional reviews and user comments.</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
