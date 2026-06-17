/* ============================================================
   Fone.ai — Utility Functions
   ============================================================ */

/**
 * Format a number as Indian Rupee currency
 * @example formatPrice(25000) → "₹25,000"
 * @example formatPrice(150000) → "₹1,50,000"
 */
export function formatPrice(amount: number | null | undefined): string {
  if (amount == null) return '₹N/A';
  
  // Indian number formatting (uses en-IN locale)
  return '₹' + amount.toLocaleString('en-IN');
}

/**
 * Format a number as compact Indian currency
 * @example formatPriceCompact(25000) → "₹25K"
 * @example formatPriceCompact(150000) → "₹1.5L"
 */
export function formatPriceCompact(amount: number): string {
  if (amount >= 100000) {
    const lakhs = amount / 100000;
    return `₹${lakhs % 1 === 0 ? lakhs : lakhs.toFixed(1)}L`;
  }
  if (amount >= 1000) {
    const thousands = amount / 1000;
    return `₹${thousands % 1 === 0 ? thousands : thousands.toFixed(1)}K`;
  }
  return `₹${amount}`;
}

/**
 * Format match score as percentage
 * @example formatMatchScore(0.87) → "87%"
 */
export function formatMatchScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/**
 * Slugify a text string
 * @example slugify("Samsung Galaxy S25 Ultra") → "samsung-galaxy-s25-ultra"
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Get price tier from price in INR
 */
export function getPriceTier(price: number): 'budget' | 'mid-range' | 'upper-mid' | 'premium' | 'flagship' {
  if (price < 15000) return 'budget';
  if (price < 25000) return 'mid-range';
  if (price < 40000) return 'upper-mid';
  if (price < 70000) return 'premium';
  return 'flagship';
}

/**
 * Get a human-readable price tier label
 */
export function getPriceTierLabel(tier: string): string {
  const labels: Record<string, string> = {
    'budget': 'Budget',
    'mid-range': 'Mid-Range',
    'upper-mid': 'Upper Mid-Range',
    'premium': 'Premium',
    'flagship': 'Flagship',
  };
  return labels[tier] || tier;
}

/**
 * Merge CSS class names, filtering out falsy values
 * @example cn('base', isActive && 'active', className) → "base active custom"
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Delay execution for a specified number of milliseconds
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Clamp a number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Format a spec value with unit
 * @example formatSpec(5000, 'mAh') → "5,000 mAh"
 * @example formatSpec(6.7, '"') → "6.7\""
 */
export function formatSpec(value: number | null | undefined, unit: string): string {
  if (value == null) return 'N/A';
  
  if (unit === '"') {
    return `${value}"`;
  }
  
  if (Number.isInteger(value)) {
    return `${value.toLocaleString('en-IN')} ${unit}`;
  }
  
  return `${value} ${unit}`;
}

/**
 * Get key specs summary for a phone
 */
export function getKeySpecs(phone: {
  chipset?: string | null;
  main_camera_mp?: number | null;
  camera_setup?: string | null;
  battery_mah?: number | null;
  charging_watts?: number | null;
  display_size?: number | null;
  refresh_rate?: number | null;
  display_type?: string | null;
  ram_gb?: number[];
  storage_gb?: number[];
}): { label: string; value: string }[] {
  const specs: { label: string; value: string }[] = [];
  
  if (phone.chipset) {
    specs.push({ label: 'Processor', value: phone.chipset });
  }
  
  if (phone.camera_setup || phone.main_camera_mp) {
    specs.push({ 
      label: 'Camera', 
      value: phone.camera_setup || `${phone.main_camera_mp}MP` 
    });
  }
  
  if (phone.battery_mah) {
    const charging = phone.charging_watts ? `, ${phone.charging_watts}W` : '';
    specs.push({ 
      label: 'Battery', 
      value: `${phone.battery_mah.toLocaleString('en-IN')} mAh${charging}` 
    });
  }
  
  if (phone.display_size) {
    const refresh = phone.refresh_rate ? `, ${phone.refresh_rate}Hz` : '';
    const type = phone.display_type ? ` ${phone.display_type}` : '';
    specs.push({ 
      label: 'Display', 
      value: `${phone.display_size}"${type}${refresh}` 
    });
  }
  
  if (phone.ram_gb?.length || phone.storage_gb?.length) {
    const ram = phone.ram_gb?.length ? `${phone.ram_gb[0]}GB` : '';
    const storage = phone.storage_gb?.length ? `${phone.storage_gb[0]}GB` : '';
    if (ram && storage) {
      specs.push({ label: 'Memory', value: `${ram} / ${storage}` });
    }
  }
  
  return specs;
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '…';
}

/**
 * Generate a color based on score (0-1)
 * Returns CSS color: green for high, yellow for mid, red for low
 */
export function getScoreColor(score: number): string {
  if (score >= 0.8) return 'var(--accent-emerald)';
  if (score >= 0.6) return 'var(--accent-amber)';
  return 'var(--accent-red)';
}

/**
 * Format relative date
 * @example formatRelativeDate("2025-01-15") → "6 months ago"
 */
export function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}
