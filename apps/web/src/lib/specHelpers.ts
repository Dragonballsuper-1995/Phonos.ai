/* ============================================================
   Phonos.ai — Spec Helpers and String Formatters
   ============================================================ */

/** Strip the brand prefix from a phone name, avoiding duplication */
export function stripBrandPrefix(fullName: string, brand: string): string {
  if (!fullName || !brand) return fullName || '';
  const escaped = brand.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return fullName.replace(new RegExp(`^${escaped}\\s*`, 'i'), '').trim();
}

/** Strip RAM/ROM specs like "(16GB RAM + 256GB)" from displayed name */
export function stripRamRom(name: string): string {
  return name
    .replace(/\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)/gi, '')
    .replace(/\s*\(\d+GB\s*\+\s*\d+GB\)/gi, '')
    .replace(/\s*\(\d+GB\s+RAM\)/gi, '')
    .trim();
}

/** Clean a display name: remove brand prefix + RAM/ROM */
export function cleanPhoneName(fullName: string, brand: string): string {
  return stripRamRom(stripBrandPrefix(fullName, brand));
}

/**
 * Extracts storage and RAM variant string (e.g. "8GB + 128GB", "8GB + 256GB", "12GB + 512GB", "16GB + 1TB").
 */
export function extractStorageVariant(phone: any): string {
  if (!phone) return '';
  const raw = phone.raw_specs || {};
  const rawName = (raw.Name || phone.fullName || phone.name || '').trim();

  // 1. Try to find parenthesized configuration in the full name (e.g. "(8GB RAM + 256GB)" or "(12GB + 512GB)")
  const nameMatch = rawName.match(/\((\d+GB(?:\s*RAM)?\s*(?:\+\s*\d+(?:GB|TB))?)\)/i);
  if (nameMatch) {
    return nameMatch[1].replace(/RAM/i, '').replace(/\s+/g, ' ').trim();
  }

  // 2. Try raw_specs Memory fields or structured specs
  const ram = (raw['Memory.RAM'] || phone.specs?.ram || '').trim();
  const storage = (raw['Memory.Storage'] || phone.specs?.storage || '').trim();

  const ramClean = ram ? ram.replace(/\s*RAM/i, '').replace(/\s+/g, '') : '';
  const storageClean = storage ? storage.replace(/\s+/g, '') : '';

  if (ramClean && storageClean) {
    return `${ramClean} + ${storageClean}`;
  } else if (storageClean) {
    return storageClean;
  } else if (ramClean) {
    return ramClean;
  }

  return '';
}

/** Categorize raw specs and structured specs into readable blocks */
export function categorizeSpecs(
  specs: any,
  rawSpecs: any
): Record<string, Record<string, string>> {
  const categories: Record<string, Record<string, string>> = {
    'Key Specifications': {},
    'Display & Design': {},
    'Performance & Platform': {},
    'Cameras & Optics': {},
    'Battery & Charging': {},
    'Connectivity & Network': {},
    'Hardware Features': {},
  };

  if (specs?.processor && specs.processor !== 'Unknown') {
    categories['Key Specifications']['Processor'] = specs.processor;
  }
  if (specs?.ram && specs.ram !== 'Unknown') {
    categories['Key Specifications']['RAM'] = specs.ram;
  }
  if (specs?.storage && specs.storage !== 'Unknown') {
    categories['Key Specifications']['Storage'] = specs.storage;
  }
  if (specs?.os && specs.os !== 'Unknown') {
    categories['Key Specifications']['Operating System'] = specs.os;
  }
  if (specs?.display && specs.display !== 'Unknown') {
    categories['Display & Design']['Display Type'] = specs.display;
  }
  if (specs?.displaySize && specs.displaySize !== 'Unknown') {
    categories['Display & Design']['Screen Size'] = specs.displaySize;
  }
  if (specs?.refreshRate && specs.refreshRate !== 'Unknown') {
    categories['Display & Design']['Refresh Rate'] = specs.refreshRate;
  }
  if (specs?.mainCamera && specs.mainCamera !== 'Unknown') {
    categories['Cameras & Optics']['Rear Camera System'] = specs.mainCamera;
  }
  if (specs?.selfieCamera && specs.selfieCamera !== 'Unknown') {
    categories['Cameras & Optics']['Front Camera'] = specs.selfieCamera;
  }
  if (specs?.battery && specs.battery !== 'Unknown') {
    categories['Battery & Charging']['Battery Capacity'] = specs.battery;
  }
  if (specs?.charging && specs.charging !== 'Unknown') {
    categories['Battery & Charging']['Charging Speed'] = specs.charging;
  }
  if (specs?.waterResistance && specs.waterResistance !== 'Unknown') {
    categories['Hardware Features']['Water Resistance'] = specs.waterResistance;
  }
  if (specs?.biometrics && specs.biometrics !== 'Unknown') {
    categories['Hardware Features']['Biometrics'] = specs.biometrics;
  }

  // Parse additional raw_specs if present
  if (rawSpecs) {
    let parsed = rawSpecs;
    if (typeof rawSpecs === 'string') {
      try {
        parsed = JSON.parse(rawSpecs);
      } catch {
        parsed = {};
      }
    }

    if (typeof parsed === 'object' && parsed !== null) {
      Object.entries(parsed).forEach(([key, value]) => {
        if (!value || value === 'Unknown' || value === 'No' || typeof value !== 'string') return;
        if (key === 'Brand' || key === 'Product_Name' || key === 'Related_Items' || key === 'Price') return;

        const cleanKey = key.replace(/_/g, ' ');
        const valStr = value.toString();
        const lowerKey = key.toLowerCase();

        if (lowerKey.includes('display') || lowerKey.includes('screen') || lowerKey.includes('resolution') || lowerKey.includes('dimension') || lowerKey.includes('weight')) {
          categories['Display & Design'][cleanKey] = valStr;
        } else if (lowerKey.includes('cpu') || lowerKey.includes('gpu') || lowerKey.includes('chipset') || lowerKey.includes('memory') || lowerKey.includes('ram') || lowerKey.includes('storage') || lowerKey.includes('os') || lowerKey.includes('platform')) {
          categories['Performance & Platform'][cleanKey] = valStr;
        } else if (lowerKey.includes('camera') || lowerKey.includes('video') || lowerKey.includes('lens') || lowerKey.includes('sensor')) {
          categories['Cameras & Optics'][cleanKey] = valStr;
        } else if (lowerKey.includes('battery') || lowerKey.includes('charging')) {
          categories['Battery & Charging'][cleanKey] = valStr;
        } else if (lowerKey.includes('network') || lowerKey.includes('wifi') || lowerKey.includes('bluetooth') || lowerKey.includes('5g') || lowerKey.includes('sim') || lowerKey.includes('usb')) {
          categories['Connectivity & Network'][cleanKey] = valStr;
        } else if (lowerKey.includes('fingerprint') || lowerKey.includes('audio') || lowerKey.includes('speaker') || lowerKey.includes('jack') || lowerKey.includes('nfc')) {
          categories['Hardware Features'][cleanKey] = valStr;
        }
      });
    }
  }

  // Remove empty category buckets
  Object.keys(categories).forEach((cat) => {
    if (Object.keys(categories[cat]).length === 0) {
      delete categories[cat];
    }
  });

  return categories;
}

export interface HardwareVector5D {
  performance: number; // 0-100
  camera: number;      // 0-100
  display: number;     // 0-100
  battery: number;     // 0-100
  build: number;       // 0-100
}

/**
 * Computes a standardized 5D hardware vector (0-100) for a phone
 * incorporating scientific benchmarks (DxOMark, Geekbench, VCX, AnTuTu, AUS) with SoC power-efficiency and display calibration.
 */
export function compute5DVector(phone: any): HardwareVector5D {
  if (!phone) {
    return { performance: 50, camera: 50, display: 50, battery: 50, build: 50 };
  }

  const rawStr = (
    JSON.stringify(phone.raw_specs || {}) +
    ' ' +
    (phone.fullName || phone.name || '') +
    ' ' +
    (phone.specs?.processor || '') +
    ' ' +
    (phone.specs?.display || '') +
    ' ' +
    (phone.specs?.charging || '') +
    ' ' +
    (phone.specs?.battery || '')
  ).toLowerCase();

  // 1. Performance / SoC (0-100)
  let perfScore = 50;
  if (phone.geekbench_multi && phone.geekbench_multi > 0) {
    perfScore = Math.min(100, Math.max(30, (phone.geekbench_multi / 10500) * 100));
  } else if (phone.antutu_v10_score && phone.antutu_v10_score > 0) {
    perfScore = Math.min(100, Math.max(30, (phone.antutu_v10_score / 3500000) * 100));
  } else {
    if (rawStr.includes('8 elite gen 5') || rawStr.includes('8 elite') || rawStr.includes('9400')) perfScore = 98;
    else if (rawStr.includes('exynos 2600') || rawStr.includes('8 gen 3') || rawStr.includes('9300')) perfScore = 93;
    else if (rawStr.includes('a18 pro')) perfScore = 92;
    else if (rawStr.includes('a18')) perfScore = 86;
    else if (rawStr.includes('8s gen 3') || rawStr.includes('8300') || rawStr.includes('7+ gen 3')) perfScore = 83;
    else if (rawStr.includes('7s gen 3') || rawStr.includes('7 gen 3') || rawStr.includes('7300') || rawStr.includes('7200')) perfScore = 76;
    else if (rawStr.includes('6 gen 1') || rawStr.includes('695') || rawStr.includes('6300')) perfScore = 60;
    else perfScore = 50;
  }

  // 2. Camera / Optics (0-100)
  let camScore = 50;
  if (phone.dxomark_camera_score && phone.dxomark_camera_score > 0) {
    camScore = Math.min(100, Math.max(30, (phone.dxomark_camera_score / 165) * 100));
  } else if (phone.vcx_camera_score && phone.vcx_camera_score > 0) {
    camScore = Math.min(100, Math.max(30, (phone.vcx_camera_score / 82) * 100));
  } else {
    let base = 50;
    if (rawStr.includes('periscope') || rawStr.includes('telephoto') || rawStr.includes('optical zoom')) base += 22;
    if (rawStr.includes('zeiss') || rawStr.includes('leica') || rawStr.includes('hasselblad')) base += 12;
    if (rawStr.includes('ois') || rawStr.includes('sensor-shift')) base += 10;
    if (rawStr.includes('200 mp') || rawStr.includes('50 mp')) base += 6;
    camScore = Math.min(100, base);
  }

  // 3. Display Quality (0-100)
  let dispScore = 50;
  let panelFeatureScore = 50;
  let panelBase = 50;
  if (rawStr.includes('ltpo') || rawStr.includes('1b colors')) panelBase += 20;
  else if (rawStr.includes('amoled') || rawStr.includes('oled') || rawStr.includes('super retina')) panelBase += 14;

  if (rawStr.includes('1440 x') || rawStr.includes('2k') || rawStr.includes('3120') || rawStr.includes('3168')) panelBase += 15;
  else if (rawStr.includes('1.5k') || rawStr.includes('2772') || rawStr.includes('2556')) panelBase += 10;

  if (rawStr.includes('165hz') || rawStr.includes('144hz')) panelBase += 15;
  else if (rawStr.includes('120hz') || rawStr.includes('120 hz')) panelBase += 12;
  else if (rawStr.includes('60hz') || rawStr.includes('60 hz') || (rawStr.includes('iphone 16') && !rawStr.includes('pro'))) panelBase -= 8; // 60Hz penalty

  panelFeatureScore = Math.min(100, Math.max(30, panelBase));

  if (phone.dxomark_display_score && phone.dxomark_display_score > 0) {
    const dxoScore = Math.min(100, Math.max(30, (phone.dxomark_display_score / 162) * 100));
    dispScore = Math.round(0.60 * dxoScore + 0.40 * panelFeatureScore);
  } else {
    dispScore = panelFeatureScore;
  }

  // 4. Power-Efficiency & Battery (0-100)
  // Chipset Node Efficiency Multiplier
  let chipEfficiency = 1.0;
  let efficiencyScore = 75;
  if (rawStr.includes('a18') || rawStr.includes('a17') || rawStr.includes('ios')) {
    chipEfficiency = 1.25; // Apple Silicon 3nm + iOS deep optimization
    efficiencyScore = 98;
  } else if (rawStr.includes('7s gen 3') || rawStr.includes('6 gen 1') || rawStr.includes('7300 energy') || rawStr.includes('7200')) {
    chipEfficiency = 1.20; // Modern low-thermal high-efficiency silicon
    efficiencyScore = 95;
  } else if (rawStr.includes('8 elite') || rawStr.includes('9400') || rawStr.includes('exynos 2600')) {
    chipEfficiency = 1.10; // Modern flagship 3nm/2nm
    efficiencyScore = 88;
  }

  // Display Refresh Efficiency Multiplier
  let dispEfficiency = 1.0;
  if (rawStr.includes('60hz') || rawStr.includes('ltpo')) {
    dispEfficiency = 1.05;
  }

  // Calculate active endurance hours
  let activeHours = 14.0;
  let capacity = 5000;
  const capMatch = rawStr.match(/(\d{4,5})\s*mah/);
  if (capMatch) capacity = parseInt(capMatch[1], 10);

  if (phone.gsmarena_battery_hours && phone.gsmarena_battery_hours > 0) {
    activeHours = phone.gsmarena_battery_hours;
  } else {
    activeHours = (capacity / 340) * chipEfficiency * dispEfficiency;
  }

  let enduranceScore = Math.min(100, Math.max(30, (activeHours / 22.0) * 100));
  if (capacity >= 9000) {
    enduranceScore = 100;
  }

  // Charging Wattage Score
  let chargingScore = 60;
  let chargeWatt = 25;
  const cMatch = rawStr.match(/(\d{2,3})\s*w/);
  if (cMatch) chargeWatt = parseInt(cMatch[1], 10);

  if (chargeWatt >= 120) chargingScore = 100;
  else if (chargeWatt >= 80) chargingScore = 92;
  else if (chargeWatt >= 60) chargingScore = 84;
  else if (chargeWatt >= 45) chargingScore = 75;
  else if (chargeWatt >= 25) chargingScore = 60;
  else chargingScore = 50;

  let batScore = Math.round(
    0.65 * enduranceScore + 0.20 * chargingScore + 0.15 * efficiencyScore
  );

  // If a phone has a massive 10,000+ mAh battery with fast charging (>= 65W), it is an absolute 100/100 monster
  if (capacity >= 9500 && chargeWatt >= 65) {
    batScore = 100;
  }

  // 5. Build & Durability (0-100)
  let buildBase = 50;
  if (rawStr.includes('ip68') || rawStr.includes('ip69')) buildBase += 25;
  else if (rawStr.includes('ip65') || rawStr.includes('ip64')) buildBase += 10;
  if (rawStr.includes('titanium')) buildBase += 15;
  else if (rawStr.includes('aluminum') || rawStr.includes('metal frame')) buildBase += 10;
  if (rawStr.includes('armor') || rawStr.includes('victus') || rawStr.includes('ceramic shield')) buildBase += 10;
  const buildScore = Math.min(100, buildBase);

  return {
    performance: Math.round(perfScore),
    camera: Math.round(camScore),
    display: Math.round(dispScore),
    battery: Math.round(batScore),
    build: Math.round(buildScore),
  };
}

export interface BalancedOverallResult {
  overallScore: number;
  balanceRating: string;
  consistency: number;
}

/**
 * Computes a Harmonic Balanced Overall Score for a phone across its 5D vector.
 * Rewards well-rounded flagships that score consistently high (8-10/10 in every category),
 * while penalizing single-spike devices that have critical shortcomings in other areas.
 */
export function computeBalancedOverallScore(v: HardwareVector5D): BalancedOverallResult {
  const scores = [v.performance, v.camera, v.display, v.battery, v.build];
  const mean = scores.reduce((sum, s) => sum + s, 0) / scores.length;
  const min = Math.min(...scores);

  // Calculate standard deviation to measure variance across categories
  const variance = scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length;
  const stdDev = Math.sqrt(variance);

  // Consistency penalty for uneven devices
  const penaltyRatio = (stdDev / 100) * (1.0 - min / 100);
  const overallScore = Math.min(100, Math.max(30, Math.round(mean * (1.0 - 0.45 * penaltyRatio))));
  const consistency = Math.max(20, Math.round(100 - stdDev * 2));

  let balanceRating = 'Well-Balanced All-Rounder';
  if (overallScore >= 92 && consistency >= 85) balanceRating = 'Flagship All-Round Champion 👑';
  else if (overallScore >= 85) balanceRating = 'Strong Multi-Category Performer';
  else if (consistency < 70) balanceRating = 'Specialized (Uneven Specs)';
  else balanceRating = 'Balanced Daily Driver';

  return {
    overallScore,
    balanceRating,
    consistency,
  };
}

export interface DeepOpticsDetails {
  sensors: string;
  lensElements: string;
  fovAndAperture: string;
  zoomCapabilities: string;
  stabilizationAndAF: string;
  videoFeatures: string;
}

/**
 * Extracts comprehensive sensor-level engineering details for the deep optics accordion drawer.
 */
export function extractDeepOptics(phone: any): DeepOpticsDetails {
  const raw = phone?.raw_specs || {};
  const rawStr = JSON.stringify(raw).toLowerCase() + ' ' + (phone?.fullName || '').toLowerCase();

  // 1. Sensors
  let sensors = '';
  const sMatches = rawStr.match(/sensor:\s*([^,\n<\)]+)/gi) || rawStr.match(/sony\s+[a-z0-9\-]+|s5k[a-z0-9]+|ov\d+[a-z]+/gi);
  if (sMatches) {
    sensors = Array.from(new Set(sMatches.map(s => s.replace(/sensor:\s*/i, '').trim()))).slice(0, 3).join(' • ');
  }
  if (!sensors) {
    if (rawStr.includes('lyt-808') || rawStr.includes('lyt-700')) sensors = 'Sony LYT Flagship Sensor System';
    else if (rawStr.includes('imx906')) sensors = 'Sony IMX906 (1/1.56") + S5KJN5';
    else if (rawStr.includes('s26')) sensors = 'Samsung ISOCELL S5K GN3/HP2 Custom Optics';
    else if (rawStr.includes('iphone 16')) sensors = 'Apple Custom 48MP Quad-Pixel Sensor';
    else sensors = 'Multi-Layer High Resolution Optical Sensors';
  }

  // 2. Lens Elements
  let lensElements = '';
  const lMatches = rawStr.match(/\d+p\s*lens|\d+p/gi);
  if (lMatches) {
    lensElements = Array.from(new Set(lMatches)).join(', ');
  } else {
    lensElements = '6P Primary Optical Elements, 5P Front Lens';
  }

  // 3. FOV & Apertures
  let fovAndAperture = '';
  const fovMatches = rawStr.match(/\d+°\s*fov|\d+°\s*field\s*of\s*view|\d+˚/gi);
  if (fovMatches) {
    fovAndAperture = Array.from(new Set(fovMatches)).join(', ');
  } else {
    fovAndAperture = 'Main 84° FOV (ƒ/1.8), Ultra Wide 116°–120° FOV (ƒ/2.2)';
  }

  // 4. Zoom
  let zoomCapabilities = '';
  if (rawStr.includes('periscope') || rawStr.includes('5x optical') || rawStr.includes('3.5x optical') || rawStr.includes('3x optical')) {
    const zMatch = rawStr.match(/(\d+\.?\d*x\s*optical(?:\s*zoom)?)/i);
    zoomCapabilities = zMatch ? `${zMatch[1].toUpperCase()} + Up to 100x Digital Zoom` : '3x–5x Optical Zoom + Up to 30x–100x Space Zoom';
  } else if (rawStr.includes('2x in-sensor') || rawStr.includes('sensor-shift') || rawStr.includes('iphone 16')) {
    zoomCapabilities = '2x Optical-Quality In-Sensor Telephoto + 10x Digital';
  } else {
    zoomCapabilities = 'Digital Zoom & Multi-Frame Super Resolution';
  }

  // 5. Stabilization & AF
  let stabilizationAndAF = '';
  const stabItems = [];
  if (rawStr.includes('sensor-shift')) stabItems.push('Sensor-Shift OIS');
  else if (rawStr.includes('ois')) stabItems.push('Hardware Optical Image Stabilization (OIS)');
  if (rawStr.includes('laser focus') || rawStr.includes('laser af')) stabItems.push('Laser Autofocus');
  if (rawStr.includes('color spectrum')) stabItems.push('Color Spectrum Sensor');
  if (rawStr.includes('pdaf') || rawStr.includes('dual pixel')) stabItems.push('Dual Pixel PDAF');
  stabilizationAndAF = stabItems.length > 0 ? stabItems.join(' • ') : 'Optical Image Stabilization (OIS) & Phase Detection Autofocus';

  // 6. Video
  let videoFeatures = '';
  if (rawStr.includes('8k')) videoFeatures = '8K UHD @ 30fps, 4K @ 60fps Dolby Vision, HDR10+, Super Steady';
  else if (rawStr.includes('dolby vision')) videoFeatures = '4K @ 60fps Dolby Vision HDR, Cinematic Mode, Action Mode';
  else videoFeatures = '4K @ 60fps UHD, 1080p @ 240fps Slo-Mo, HDR Video';

  return {
    sensors,
    lensElements,
    fovAndAperture,
    zoomCapabilities,
    stabilizationAndAF,
    videoFeatures,
  };
}


