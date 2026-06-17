/* ============================================================
   Fone.ai — TypeScript Type Definitions
   ============================================================ */

// ---- Phone & Specs ----

export interface PhoneSpecs {
  display: string;
  displaySize: string;
  refreshRate: string;
  processor: string;
  ram: string;
  storage: string;
  expandableStorage: boolean;
  mainCamera: string;
  selfieCamera: string;
  battery: string;
  charging: string;
  os: string;
  connectivity5G: boolean;
  weight: string;
  dimensions: string;
  waterResistance: string;
  nfc: boolean;
  biometrics: string;
}

export interface Phone {
  id: string;
  slug: string;
  brand: string;
  model: string;
  fullName: string;
  price: number;
  imageUrl?: string;
  specs: PhoneSpecs;
  releaseDate?: string;
  priceTier: PriceTier;
  highlights: string[];
  buyLinks?: BuyLink[];
}

export interface BuyLink {
  store: string;
  url: string;
  price: number;
}

// ---- Recommendations ----

export interface Recommendation {
  phone: Phone;
  matchScore: number; // 0-100
  explanation: string;
  strengths: string[];
  weaknesses: string[];
  categoryScores: CategoryScore[];
}

export interface CategoryScore {
  category: string;
  score: number; // 0-100
  label: string;
}

export interface RecommendationResponse {
  recommendations: Recommendation[];
  totalPhonesAnalyzed: number;
  queryParams: QueryParams;
}

// ---- Query Parameters ----

export interface EasyModeParams {
  persona: PersonaType;
  budgetMin: number;
  budgetMax: number;
  brandPreferences: string[];
  features: string[];
}

export interface MediumModeParams {
  priorities: PriorityRanking[];
  budgetMin: number;
  budgetMax: number;
  osPreference: OSPreference;
  brandPreferences: string[];
}

export interface PriorityRanking {
  feature: FeatureType;
  rank: number; // 1 = highest priority
}

export type QueryParams = EasyModeParams | MediumModeParams;

// ---- Enums & Union Types ----

export type PersonaType =
  | 'student'
  | 'professional'
  | 'gamer'
  | 'content-creator'
  | 'senior'
  | 'photography'
  | 'general';

export type PriceTier = 'budget' | 'mid-range' | 'premium' | 'flagship';

export type OSPreference = 'android' | 'ios' | 'any';

export type FeatureType =
  | 'camera'
  | 'performance'
  | 'battery'
  | 'display'
  | 'storage'
  | 'build'
  | 'value';

export type QuickFeature =
  | '5g'
  | 'big-battery'
  | 'fast-charging'
  | 'expandable-storage'
  | 'waterproof'
  | 'wireless-charging';

// ---- UI Types ----

export interface Persona {
  id: PersonaType;
  name: string;
  icon: string;
  description: string;
  color: string;
}

export interface Feature {
  id: FeatureType;
  name: string;
  icon: string;
  description: string;
}

export interface QuickFeatureOption {
  id: QuickFeature;
  name: string;
  icon: string;
}

export interface Brand {
  id: string;
  name: string;
  logo?: string;
}

export interface PriceTierOption {
  id: string;
  label: string;
  min: number;
  max: number;
}

// ---- Comparison ----

export interface CompareResult {
  phones: Phone[];
  specComparison: SpecComparisonRow[];
  winners: Record<string, string>; // category → phone id
}

export interface SpecComparisonRow {
  label: string;
  category: string;
  values: Record<string, string>; // phone id → value
  winnerId?: string;
}

// ---- API Response Wrappers ----

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ---- Theme ----

export type Theme = 'dark' | 'light';

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}
