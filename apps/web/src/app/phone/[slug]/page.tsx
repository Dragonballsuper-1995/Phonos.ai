import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { api } from '@/lib/api';
import PhoneReport from '@/components/phone/PhoneReport';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const decoded = decodeURIComponent(slug);
  return {
    title: `${decoded} — Hardware Intelligence Report | Phonos.ai`,
    description: `Comprehensive specifications, verified Indian pricing, and capability ratings for ${decoded}.`,
  };
}

export default async function PhonePage({ params }: PageProps) {
  const { slug } = await params;
  const decodedSlug = decodeURIComponent(slug);

  let phone;
  try {
    phone = await api.getPhone(decodedSlug);
  } catch (err) {
    console.error(`Phone not found: ${decodedSlug}`, err);
    notFound();
  }

  if (!phone) {
    notFound();
  }

  return (
    <main>
      <PhoneReport phone={phone} />
    </main>
  );
}
