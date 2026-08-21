/* ============================================================
   Phonos.ai — Constants
   ============================================================ */

import type { Persona } from './types';

// ---- API Base URL ----
const cleanBaseUrl = (process.env.NEXT_PUBLIC_API_URL || '').trim().replace(/\/+$/, '');
export const API_BASE_URL = cleanBaseUrl
  ? (cleanBaseUrl.endsWith('/api/v1') ? cleanBaseUrl : `${cleanBaseUrl}/api/v1`)
  : 'http://localhost:8000/api/v1';

// ---- Personas (Easy Mode) ----
export const PERSONAS: Persona[] = [
  {
    id: 'student',
    name: 'Student',
    description: 'High value, reliable battery, and social-first cameras on a realistic budget.',
  },
  {
    id: 'professional',
    name: 'Professional',
    description: 'Sleek design, flawless multi-tasking, fast charging, and dependable security.',
  },
  {
    id: 'gamer',
    name: 'Gamer',
    description: 'Maximum raw chipset compute, thermal stability, and high refresh displays.',
  },
  {
    id: 'content-creator',
    name: 'Content Creator',
    description: '4K stabilized video, high-resolution sensors, and generous onboard storage.',
  },
  {
    id: 'photography',
    name: 'Photography',
    description: 'Flagship optics, natural color science, dynamic range, and low-light prowess.',
  },
  {
    id: 'general',
    name: 'General Use',
    description: 'Clean software, all-day stamina, and dependable durability for everyday life.',
  },
  {
    id: 'senior',
    name: 'Senior',
    description: 'Crisp display legibility, loud dual speakers, intuitive UI, and long battery life.',
  },
];

// ---- Medium Mode Aspects ----
export const HEURISTIC_ASPECTS = [
  { key: 'performance', label: 'Performance', description: 'CPU speed, gaming, daily responsiveness' },
  { key: 'camera', label: 'Camera', description: 'Photo quality, sensor size, video clarity' },
  { key: 'battery', label: 'Battery', description: 'Endurance, screen-on time, fast charge rate' },
  { key: 'display', label: 'Display', description: 'OLED/AMOLED, brightness, 120Hz refresh' },
  { key: 'value', label: 'Value', description: 'Price-to-specification ratio in Indian rupees' },
] as const;

// ---- Budget Configuration ----
export const BUDGET_MIN = 5000;
export const BUDGET_MAX = 150000;
export const BUDGET_STEP = 1000;
export const BUDGET_DEFAULT = 35000;

// ---- Modes ----
export const MODES = [
  {
    id: 'easy',
    name: 'Easy',
    tagline: 'Persona & Budget',
    description: 'Select your lifestyle profile and allocation limit. The engine filters and ranks verified candidates in two quick steps.',
    href: '/easy',
    badge: '2 STEPS',
  },
  {
    id: 'medium',
    name: 'Medium',
    tagline: 'Parameter Control',
    description: 'Fine-tune precise heuristic weights for performance, camera, battery, display, and value to match exact demands.',
    href: '/medium',
    badge: 'EXACT WEIGHTS',
  },
  {
    id: 'deep',
    name: 'Deep',
    tagline: 'Neural Search',
    description: 'Describe requirements in natural language. Semantic vector embeddings extract latent constraints automatically.',
    href: '/deep',
    badge: 'NATURAL LANGUAGE',
  },
  {
    id: 'compare',
    name: 'Compare',
    tagline: '5D Radar & Benchmarks',
    description: 'Side-by-side technical matrix comparing performance, cameras, battery life, DxOMark lab scores, and 5D radar.',
    href: '/compare',
    badge: '5D RADAR MATRIX',
  },
] as const;
