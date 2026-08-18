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
