import { ads as localAds } from '../data/adContent';
import partnerAdsData from '../data/partner_ads.json';

// Define the unified Ad interface
export interface Ad {
  id?: string;
  title: string;
  desc: string;
  image: string;
  link: string;
  cta: string;
  badges: { text: string; color: string }[];
  overlayTitle?: string;
}

// Helper to Map External Spot Data to Ad Format
function mapSpotToAd(city: string, spot: any): Ad {
  return {
    id: `surf-${city}-${spot.name}`,
    title: `露營累了嗎？來去${spot.name}衝浪吧！`,
    overlayTitle: `推薦${city}衝浪`,
    desc: spot.desc || `位於${city}的優質浪點，享受大海與衝浪體驗。`,
    image: spot.image && spot.image !== '' ? spot.image : '/go-surf.webp',
    link: spot.link || '#',
    cta: `查看${spot.name}`,
    badges: [
      { text: '🤝 夥伴推薦', color: 'blue' },
      { text: '露營 x 衝浪', color: 'orange' }
    ]
  };
}

// Cache the Source of External Ads
let _cachedExternalSource: Ad[] | null = null;

function getExternalAdsSource(): Ad[] {
   if (_cachedExternalSource) return _cachedExternalSource;
   const list: Ad[] = [];
   const inventory = partnerAdsData as Record<string, any[]>;
   Object.entries(inventory).forEach(([city, spots]) => {
     spots.forEach(spot => list.push(mapSpotToAd(city, spot)));
   });
   _cachedExternalSource = list;
   return list;
}

export function getAllAds(): Ad[] {
  // 1. Get All Potential External Ads
  const allExternal = [...getExternalAdsSource()];
  
  // 2. Randomly Select 3 External Ads (Fisher-Yates Shuffle)
  for (let i = allExternal.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [allExternal[i], allExternal[j]] = [allExternal[j], allExternal[i]];
  }
  const selectedExternal = allExternal.slice(0, 3);

  // 3. Combine with All Local Ads (No Caching, to ensure variety per page build)
  const combined = [...localAds, ...selectedExternal];
  
  // Map local ads to ensure they conform to Ad interface completely (optional but safe)
  return combined.map(ad => ({
      ...ad,
      // Ensure badges have correct shape if not already
      badges: ad.badges.map(b => ({text: b.text, color: b.color})),
      cta: ad.cta || '查看詳情',
      link: ad.link || '#'
  })) as Ad[];
}

export function getShuffledAds(): Ad[] {
  const ads = [...getAllAds()];
  // Fisher-Yates Shuffle
  for (let i = ads.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [ads[i], ads[j]] = [ads[j], ads[i]];
  }
  return ads;
}

/**
 * Returns a cyclical iterator for the ads, starting at a random index.
 */
export function getAdRotator() {
  const ads = getShuffledAds();
  const startIndex = Math.floor(Math.random() * ads.length);
  let currentIndex = startIndex;

  return {
    next: () => {
        if (ads.length === 0) return null;
        const ad = ads[currentIndex];
        currentIndex = (currentIndex + 1) % ads.length;
        return ad;
    },
    getAll: () => ads // Exposed for client-side usage if needed
  };
}
