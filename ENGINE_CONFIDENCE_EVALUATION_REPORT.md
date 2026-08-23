# Phonos.ai Recommendation Engine — Confidence & Quality Benchmark Report
**Generated on:** `2026-08-23 20:35:48`  
**Engine Architecture:** 4-Stage Hybrid (Vector Search + Knowledge Graph + XGBoost Ranker + ABSA Sentiment + AI Verification)  

---

## 1. Executive Summary & Confidence Scorecard

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Constraint Validity Rate (CVR)** | **100.0%** | $\ge 99.0\%$ | ✅ PASS |
| **Phantom Device Exclusion Rate** | **100.0%** | $100.0\%$ | ✅ PASS |
| **Mean Recommendation Confidence (RCS)** | **0.9745 / 1.0** | $\ge 0.820$ | ✅ PASS |
| **Expected Calibration Error (ECE)** | **0.0255** | $< 0.080$ | ✅ PASS |
| **Brier Calibration Score** | **0.0012** | $< 0.100$ | ✅ PASS |
| **Persona Congruency Index (PCI)** | **0.8087 / 1.0** | $\ge 0.800$ | ✅ PASS |
| **Spec Grounding & Fact Fidelity** | **100.0%** | $\ge 98.0\%$ | ✅ PASS |
| **Brand Diversity (Shannon Entropy)** | **1.2692** | $\ge 1.000$ | ✅ PASS |
| **Average Response Latency (Excl. LLM)**| **182.4 ms** | $< 300\text{ ms}$ | ✅ PASS |

---

## 2. Confidence Calibration & Reliability Analysis (ECE)

Confidence calibration measures whether a confidence score of 90% actually corresponds to a 90% empirical success and satisfaction rate.

| Confidence Bin | Sample Count | Avg Confidence | Empirical Accuracy | Calibration Gap (|Acc - Conf|) |
| :--- | :--- | :--- | :--- | :--- |
| `0.90 - 1.00` | 110 | 0.975 | 1.000 | 0.025 |

**Global Expected Calibration Error (ECE):** `0.0255`  
**Maximum Calibration Error (MCE):** `0.0255`  
**Brier Score:** `0.0012`

---

## 3. Detailed Evaluation Scenarios Breakdown

| ID | Category & User Intent | Budget (₹) | Top Recommended Device | RCS Confidence | PCI Fit | Diversity (Brands) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EASY-01` | Student Entry (₹10,000) | ₹10,000 | **Oppo Oppo A5x 4G** | `0.950` | `0.62` | 4 brands | **PASS** |
| `EASY-02` | Student Mid-Range (₹20,000) | ₹20,000 | **Samsung Samsung Galaxy F70e** | `0.973` | `0.74` | 3 brands | **PASS** |
| `EASY-03` | Gamer Budget (₹25,000) | ₹25,000 | **Poco Poco X7 5G** | `0.960` | `0.78` | 3 brands | **PASS** |
| `EASY-04` | Gamer Mid-Flagship (₹45,000) | ₹45,000 | **OnePlus OnePlus 15R 5G** | `0.995` | `0.86` | 3 brands | **PASS** |
| `EASY-05` | Gamer Ultra Flagship (₹90,000) | ₹90,000 | **OnePlus OnePlus 15 5G** | `0.995` | `0.93` | 4 brands | **PASS** |
| `EASY-06` | Creator Mid-Range (₹35,000) | ₹35,000 | **Poco Poco X8 Pro Max 5G** | `0.995` | `0.79` | 4 brands | **PASS** |
| `EASY-07` | Creator Premium (₹60,000) | ₹60,000 | **Vivo Vivo X300 FE** | `0.990` | `0.90` | 3 brands | **PASS** |
| `EASY-08` | Creator Flagship Studio (₹1,20,000) | ₹120,000 | **OnePlus OnePlus 13 (24GB RAM+ 1TB)** | `0.950` | `0.94` | 4 brands | **PASS** |
| `EASY-09` | Executive / Business (₹70,000) | ₹70,000 | **OnePlus OnePlus 13** | `0.995` | `0.89` | 4 brands | **PASS** |
| `EASY-10` | Clean OS Purist (₹32,000) | ₹32,000 | **Motorola Motorola Edge 70 Fusion 5G** | `0.938` | `0.93` | 4 brands | **PASS** |
| `EASY-11` | Senior / Basic Usability (₹12,000) | ₹12,000 | **HMD HMD Crest Max** | `0.948` | `0.68` | 3 brands | **PASS** |
| `MED-01` | Medium - 80% Performance Focus | ₹30,000 | **Samsung Samsung Galaxy F36 5G** | `0.995` | `0.76` | 3 brands | **PASS** |
| `MED-02` | Medium - 80% Battery Focus | ₹22,000 | **realme Realme P4R 5G** | `0.960` | `0.71` | 3 brands | **PASS** |
| `MED-03` | Medium - 80% Camera Focus | ₹50,000 | **iQOO IQOO 15R** | `0.995` | `0.81` | 4 brands | **PASS** |
| `MED-04` | Medium - Balanced All-Rounder | ₹40,000 | **Samsung Samsung Galaxy F70 Pro 5G** | `0.995` | `0.80` | 5 brands | **PASS** |
| `MED-05` | Medium - Display & Build Focus | ₹65,000 | **OnePlus OnePlus 13** | `0.995` | `0.86` | 4 brands | **PASS** |
| `DEEP-01` | Deep - Compact Flagship Query | ₹85,000 | **OnePlus OnePlus 15 5G** | `0.995` | `0.86` | 4 brands | **PASS** |
| `DEEP-02` | Deep - Clean Stock OS with Fast Charge | ₹35,000 | **Motorola Motorola Edge 70 Fusion 5G** | `0.938` | `0.88` | 4 brands | **PASS** |
| `DEEP-03` | Deep - 4K120 Vlogging Telephoto | ₹75,000 | **OnePlus OnePlus 13** | `0.995` | `0.93` | 4 brands | **PASS** |
| `EDGE-01` | Edge Case - Ultra Luxury ₹2,00,000 | ₹200,000 | **Motorola Motorola Razr Fold** | `0.995` | `0.87` | 5 brands | **PASS** |
| `EDGE-02` | Edge Case - Ultra Low ₹8,000 | ₹8,000 | **Poco POCO C85 5G** | `0.995` | `0.60` | 4 brands | **PASS** |
| `EDGE-03` | Edge Case - Dynamic Floor Squeeze ₹18,000 | ₹18,000 | **Samsung Samsung Galaxy F70e** | `0.990` | `0.65` | 4 brands | **PASS** |

---

## 4. Pillar-by-Pillar Confidence Architecture

Phonos.ai computes recommendation confidence through 5 deterministic pillars:

1. **Constraint Validity (30% weight)**: Strict budget compliance (105% tolerance ceiling), dynamic price floor ($0.65 \times \text{budget}$), 2024–2026 launch year recency, zero phantom models.
2. **Persona & Hardware Alignment (25% weight)**: Silicon tier, camera optics, display refresh rate, and battery endurance matched against user persona.
3. **Spec Grounding Fidelity (20% weight)**: Fact-checking that all claims in recommendation pitches match verifiable hardware specs.
4. **Market Authenticity (15% weight)**: Official active selling catalog status and Indian retail validation.
5. **Sentiment & Consensus (10% weight)**: Aspect-Based Sentiment Analysis (ABSA) extracted from reviewer testing.
