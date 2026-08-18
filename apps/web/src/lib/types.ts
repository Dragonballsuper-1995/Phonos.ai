/* ============================================================
   Phonos.ai — TypeScript Type Definitions
   Aligned with FastAPI backend models & DESIGN.md
   ============================================================ */

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

export interface PhoneDetails {
  id?: number;
  slug: string;
  brand: string;
  model: string;
  fullName: string;
  price: number;
  imageUrl?: string | null;
  specs: PhoneSpecs;
  releaseDate?: string | null;
  priceTier: string;
  highlights: string[];
  name?: string;
  price_numeric?: number;
  released_in_india?: number;
  launch_year?: number;
  raw_specs?: Record<string, any>;
}

// Alias for convenience
export type Phone = PhoneDetails;

export interface RecommendedPhone {
  phone: PhoneDetails;
  score: number; // 0-100
  match_reasons: string[];
  trade_offs: string[];
  ai_verified: boolean;
  verify_reason?: string | null;
  ai_explanation?: string | null;
}

export interface RecommendationResponse {
  recommendations: RecommendedPhone[];
  persona_detected?: string | null;
  budget_used: number;
}

// ---- Query Requests ----

export interface EasyRecommendRequest {
  persona: string;
  budget: number;
}

export interface MediumRecommendRequest {
  budget: number;
  priorities: Record<string, number>;
  preferences?: string[];
  preferred_brands?: string[];
  avoid_brands?: string[];
}

export interface DeepRecommendRequest {
  query: string;
  budget?: number;
}

// ---- Persona UI Types ----

export interface Persona {
  id: string;
  name: string;
  description: string;
}
