/* ============================================================
   Fone.ai — Constants
   ============================================================ */

import type {
  Persona,
  Feature,
  QuickFeatureOption,
  Brand,
  PriceTierOption,
} from './types';

// ---- API ----

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1`
    : 'http://localhost:8000/api/v1';

// ---- Personas ----

export const PERSONAS: Persona[] = [
  {
    id: 'student',
    name: 'Student',
    icon: '🎓',
    description: 'Best value for college life — notes, socials, and everything in between',
    color: '#6366F1',
  },
  {
    id: 'professional',
    name: 'Professional',
    icon: '💼',
    description: 'Productivity powerhouse for emails, calls, and multitasking',
    color: '#8B5CF6',
  },
  {
    id: 'gamer',
    name: 'Gamer',
    icon: '🎮',
    description: 'High-performance gaming with smooth framerates and cooling',
    color: '#EC4899',
  },
  {
    id: 'content-creator',
    name: 'Content Creator',
    icon: '🎬',
    description: 'Create stunning content with top cameras and editing power',
    color: '#06B6D4',
  },
  {
    id: 'senior',
    name: 'Senior',
    icon: '👴',
    description: 'Easy-to-use, big display, loud speakers, long battery life',
    color: '#10B981',
  },
  {
    id: 'photography',
    name: 'Photography',
    icon: '📸',
    description: 'DSLR-level photos with flagship camera systems',
    color: '#F59E0B',
  },
  {
    id: 'general',
    name: 'General Use',
    icon: '📱',
    description: 'A well-rounded phone for everyday needs',
    color: '#A78BFA',
  },
];

// ---- Features (for priority ranking) ----

export const FEATURES: Feature[] = [
  {
    id: 'camera',
    name: 'Camera',
    icon: '📷',
    description: 'Photo and video quality',
  },
  {
    id: 'performance',
    name: 'Performance',
    icon: '⚡',
    description: 'Speed, multitasking, gaming',
  },
  {
    id: 'battery',
    name: 'Battery',
    icon: '🔋',
    description: 'Battery life and charging speed',
  },
  {
    id: 'display',
    name: 'Display',
    icon: '🖥️',
    description: 'Screen quality, size, and refresh rate',
  },
  {
    id: 'storage',
    name: 'Storage',
    icon: '💾',
    description: 'RAM and internal storage capacity',
  },
  {
    id: 'build',
    name: 'Build Quality',
    icon: '🛡️',
    description: 'Materials, water resistance, durability',
  },
  {
    id: 'value',
    name: 'Value for Money',
    icon: '💰',
    description: 'Best specs at the lowest price',
  },
];

// ---- Quick Features (Easy Mode chips) ----

export const QUICK_FEATURES: QuickFeatureOption[] = [
  { id: '5g', name: '5G Connectivity', icon: '📡' },
  { id: 'big-battery', name: 'Big Battery (5000mAh+)', icon: '🔋' },
  { id: 'fast-charging', name: 'Fast Charging (65W+)', icon: '⚡' },
  { id: 'expandable-storage', name: 'Expandable Storage', icon: '💾' },
  { id: 'waterproof', name: 'Water Resistant', icon: '💧' },
  { id: 'wireless-charging', name: 'Wireless Charging', icon: '🔌' },
];

// ---- Brands (Indian market) ----

export const BRANDS: Brand[] = [
  { id: 'samsung', name: 'Samsung' },
  { id: 'apple', name: 'Apple' },
  { id: 'oneplus', name: 'OnePlus' },
  { id: 'xiaomi', name: 'Xiaomi' },
  { id: 'realme', name: 'Realme' },
  { id: 'vivo', name: 'Vivo' },
  { id: 'oppo', name: 'OPPO' },
  { id: 'motorola', name: 'Motorola' },
  { id: 'nothing', name: 'Nothing' },
  { id: 'google', name: 'Google' },
  { id: 'iqoo', name: 'iQOO' },
  { id: 'poco', name: 'POCO' },
  { id: 'nokia', name: 'Nokia' },
  { id: 'asus', name: 'ASUS' },
  { id: 'sony', name: 'Sony' },
  { id: 'tecno', name: 'Tecno' },
];

// ---- Price Tiers ----

export const PRICE_TIERS: PriceTierOption[] = [
  { id: 'budget', label: 'Under ₹15K', min: 5000, max: 15000 },
  { id: 'mid-range', label: '₹15K – ₹25K', min: 15000, max: 25000 },
  { id: 'premium', label: '₹25K – ₹40K', min: 25000, max: 40000 },
  { id: 'upper-premium', label: '₹40K – ₹60K', min: 40000, max: 60000 },
  { id: 'flagship', label: '₹60K+', min: 60000, max: 150000 },
];

// ---- Budget Limits ----

export const BUDGET_MIN = 5000;
export const BUDGET_MAX = 150000;
export const BUDGET_STEP = 1000;

// ---- Navigation ----

export const NAV_LINKS = [
  { label: 'Home', href: '/' },
  { label: 'Easy', href: '/easy' },
  { label: 'Medium', href: '/medium' },
  { label: 'Deep', href: '/deep' },
] as const;

// ---- Mode Descriptions ----

export const MODES = [
  {
    id: 'easy',
    title: 'Easy Mode',
    subtitle: '60 seconds',
    description: 'Answer 4 quick questions and we\'ll find your perfect phone. Great for people who know what they want.',
    icon: '🚀',
    href: '/easy',
    gradient: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
  },
  {
    id: 'medium',
    title: 'Medium Mode',
    subtitle: '2-3 minutes',
    description: 'Rank your priorities and fine-tune your preferences. Best for people who want more control.',
    icon: '🎯',
    href: '/medium',
    gradient: 'linear-gradient(135deg, #8B5CF6, #EC4899)',
  },
  {
    id: 'deep',
    title: 'Deep Mode',
    subtitle: 'Coming Soon',
    description: 'AI-powered chat that understands your lifestyle and recommends phones tailored just for you.',
    icon: '🧠',
    href: '/deep',
    gradient: 'linear-gradient(135deg, #EC4899, #F59E0B)',
  },
] as const;
