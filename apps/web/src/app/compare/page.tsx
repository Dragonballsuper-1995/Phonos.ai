'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatPrice } from '@/lib/utils';
import styles from './compare.module.css';

// Mock data
const MOCK_PHONES = [
  {
    id: 'p1',
    fullName: 'Galaxy S24 Ultra',
    brand: 'Samsung',
    price: 129999,
    imageUrl: 'https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-ultra-5g-sm-s928-u.jpg',
    specs: {
      display: '6.8" AMOLED, 120Hz',
      processor: 'Snapdragon 8 Gen 3',
      ram: '12GB',
      storage: '256GB / 512GB / 1TB',
      mainCamera: '200MP Main + 50MP Peri',
      battery: '5000 mAh, 45W',
      os: 'Android 14',
    }
  },
  {
    id: 'p2',
    fullName: 'iPhone 15 Pro Max',
    brand: 'Apple',
    price: 159900,
    imageUrl: 'https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15-pro-max.jpg',
    specs: {
      display: '6.7" OLED, 120Hz',
      processor: 'A17 Pro',
      ram: '8GB',
      storage: '256GB / 512GB / 1TB',
      mainCamera: '48MP Main + 12MP Peri',
      battery: '4422 mAh, 27W',
      os: 'iOS 17',
    }
  }
];

const SPEC_KEYS = [
  { key: 'display', label: 'Display' },
  { key: 'processor', label: 'Processor' },
  { key: 'ram', label: 'RAM' },
  { key: 'storage', label: 'Storage' },
  { key: 'mainCamera', label: 'Camera' },
  { key: 'battery', label: 'Battery' },
  { key: 'os', label: 'OS' }
];

function CompareContent() {
  const searchParams = useSearchParams();
  const [phones, setPhones] = useState(MOCK_PHONES);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Compare Phones</h1>
        <p>Side-by-side spec comparison to help you decide.</p>
      </div>

      <div className={styles.compareContainer}>
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.featureCol}>Features</th>
                {phones.map(phone => (
                  <th key={phone.id} className={styles.phoneCol}>
                    <div className={styles.phoneHeader}>
                      <div className={styles.imageWrapper}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={phone.imageUrl} alt={phone.fullName} className={styles.image} />
                      </div>
                      <div className={styles.brand}>{phone.brand}</div>
                      <Link href={`/phone/${phone.id}`} className={styles.nameLink}>
                        {phone.fullName}
                      </Link>
                      <div className={styles.price}>{formatPrice(phone.price)}</div>
                    </div>
                  </th>
                ))}
                {phones.length < 3 && (
                  <th className={styles.addCol}>
                    <Card className={styles.addCard}>
                      <div className={styles.addIcon}>+</div>
                      <span>Add Phone</span>
                    </Card>
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {SPEC_KEYS.map(({ key, label }) => (
                <tr key={key} className={styles.tableRow}>
                  <td className={styles.specLabel}>{label}</td>
                  {phones.map(phone => (
                    <td key={`${phone.id}-${key}`} className={styles.specValue}>
                      {(phone.specs as any)[key]}
                    </td>
                  ))}
                  {phones.length < 3 && <td></td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className={styles.actions}>
        <Button variant="outline" onClick={() => window.history.back()}>
          ← Back
        </Button>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className={styles.container}>Loading comparison...</div>}>
      <CompareContent />
    </Suspense>
  );
}
