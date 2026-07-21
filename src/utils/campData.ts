// src/utils/campData.ts
// ------------------------------------------------------------------
// 純函式資料工具 (Pure data helpers)
// 目標: 用「既有真實資料」自動計算出每頁獨特、有用的資訊,
//       取代模板化 prose。營區頁與 Hub 頁共用。零外部依賴、確定性。
// ------------------------------------------------------------------

export interface CampFeatures {
  has_glamping?: boolean;
  pet_friendly?: boolean;
  high_altitude?: boolean;
}

export interface Camp {
  name: string;
  city: string;
  area?: string;
  address?: string;
  lat?: number;
  lng?: number;
  elevation?: number;
  tags?: string[];
  features?: CampFeatures;
  description?: string;
  release_date?: string;
  phone?: string;
  image?: string;
}

export interface DailyWeather {
  date: string;
  max_temp: number;
  min_temp: number;
  rain_prob: number;
  uv_index?: number;
  label: string;
  icon?: string;
}

// ------------------------------------------------------------------
// 1. 海拔 → 氣候帶 (由真實 elevation 計算)
// ------------------------------------------------------------------
export function getClimateBand(elevation: number | undefined): {
  label: string;
  desc: string;
} {
  const e = elevation ?? 0;
  if (e >= 1500) {
    return { label: '高山冷涼帶', desc: `海拔 ${e} 公尺,即使盛夏白天也涼爽,日夜溫差大,入夜需備保暖衣物。` };
  }
  if (e >= 1000) {
    return { label: '中高海拔避暑帶', desc: `海拔 ${e} 公尺,夏季明顯比平地涼爽,是天然避暑選擇,秋冬易見雲海。` };
  }
  if (e >= 500) {
    return { label: '中海拔宜人帶', desc: `海拔 ${e} 公尺,氣候溫和宜人,四季皆適合出遊。` };
  }
  return { label: '低海拔溫暖帶', desc: `海拔 ${e} 公尺,氣候溫暖,交通通常較便利,適合露營新手。` };
}

// ------------------------------------------------------------------
// 2. 標籤/特徵 + 當月 → 最佳造訪季節
//    只根據真實 tags 判斷,不硬掰。
// ------------------------------------------------------------------
interface SeasonRule {
  key: string;              // 對應的 tag 關鍵字
  label: string;            // 顯示名稱
  months: number[];         // 適合月份
  reason: string;
}

const SEASON_RULES: SeasonRule[] = [
  { key: '螢火蟲', label: '賞螢季', months: [4, 5], reason: '4-5 月螢火蟲大發生,入夜後山區螢光點點。' },
  { key: '櫻花',   label: '櫻花季', months: [2, 3], reason: '2-3 月櫻花盛開,是賞櫻露營的熱門時段。' },
  { key: '賞楓',   label: '賞楓季', months: [11, 12], reason: '11-12 月楓紅,適合搭配秋季露營。' },
  { key: '楓',     label: '賞楓季', months: [11, 12], reason: '11-12 月楓葉轉紅。' },
  { key: '雲海',   label: '雲海季', months: [10, 11, 12, 1, 2, 3], reason: '秋冬清晨溫差大,是觀賞雲海的最佳季節。' },
  { key: '戲水',   label: '戲水季', months: [6, 7, 8, 9], reason: '夏季適合溪邊戲水消暑。' },
  { key: '溪流',   label: '戲水季', months: [6, 7, 8, 9], reason: '夏季溪流沁涼,適合親水活動。' },
];

// 回傳此營區「適合的季節活動」清單(去重)
export function getSeasons(camp: Camp): SeasonRule[] {
  const tags = camp.tags ?? [];
  const seen = new Set<string>();
  const out: SeasonRule[] = [];
  for (const rule of SEASON_RULES) {
    if (tags.some((t) => t.includes(rule.key)) && !seen.has(rule.label)) {
      seen.add(rule.label);
      out.push(rule);
    }
  }
  // 高海拔營區 = 夏季避暑
  if (camp.features?.high_altitude && !seen.has('避暑季')) {
    out.push({ key: 'high_altitude', label: '避暑季', months: [6, 7, 8, 9], reason: '高海拔夏季涼爽,是避暑露營首選。' });
  }
  return out;
}

// 此營區「現在(某月)是否當季」
export function isInSeason(camp: Camp, month: number): boolean {
  return getSeasons(camp).some((s) => s.months.includes(month));
}

// 產生「最佳造訪月份」摘要句(給營區頁資料塊用)
export function getBestMonthsSummary(camp: Camp): string | null {
  const seasons = getSeasons(camp);
  if (seasons.length === 0) return null;
  return seasons.map((s) => `${s.label}(${s.months.join('、')} 月)`).join('、');
}

// ------------------------------------------------------------------
// 3. 一組營區的統計 (給 Hub 頁資料佐證導言用)
// ------------------------------------------------------------------
export function getElevationStats(camps: Camp[]): {
  count: number;
  highAltitude: number;
  glamping: number;
  petFriendly: number;
  forest: number;
  minElev: number;
  maxElev: number;
  avgElev: number;
} {
  const count = camps.length;
  const elevs = camps.map((c) => c.elevation ?? 0).filter((e) => e > 0);
  const forest = camps.filter((c) => (c.tags ?? []).some((t) => t.includes('森林') || t.includes('樹林'))).length;
  return {
    count,
    highAltitude: camps.filter((c) => c.features?.high_altitude).length,
    glamping: camps.filter((c) => c.features?.has_glamping).length,
    petFriendly: camps.filter((c) => c.features?.pet_friendly).length,
    forest,
    minElev: elevs.length ? Math.min(...elevs) : 0,
    maxElev: elevs.length ? Math.max(...elevs) : 0,
    avgElev: elevs.length ? Math.round(elevs.reduce((a, b) => a + b, 0) / elevs.length) : 0,
  };
}

// ------------------------------------------------------------------
// 4. 天氣摘要 (由 weather_forecast.json 的 daily[] 計算)
// ------------------------------------------------------------------
// 單一營區:未來數日溫度區間 + 是否有雨
export function summarizeCampWeather(daily: DailyWeather[] | undefined, days = 3): string | null {
  if (!daily || daily.length === 0) return null;
  const slice = daily.slice(0, days);
  const maxT = Math.round(Math.max(...slice.map((d) => d.max_temp)));
  const minT = Math.round(Math.min(...slice.map((d) => d.min_temp)));
  const rainy = slice.filter((d) => d.rain_prob >= 50);
  let s = `未來 ${slice.length} 天氣溫約 ${minT}–${maxT}°C`;
  if (rainy.length === 0) s += ',降雨機率低。';
  else if (rainy.length >= slice.length) s += ',這幾天有雨,記得防水裝備。';
  else s += `,其中 ${rainy.length} 天有雨,建議留意天氣。`;
  return s;
}

// 一群營區(同城市):區域天氣摘要
export function summarizeRegionWeather(
  weatherMap: Record<string, { daily?: DailyWeather[] }>,
  camps: Camp[],
  cityName: string,
  days = 3,
): string | null {
  const allDaily: DailyWeather[] = [];
  for (const c of camps) {
    const w = weatherMap[c.name];
    if (w?.daily) allDaily.push(...w.daily.slice(0, days));
  }
  if (allDaily.length === 0) return null;
  const maxT = Math.round(Math.max(...allDaily.map((d) => d.max_temp)));
  const minT = Math.round(Math.min(...allDaily.map((d) => d.min_temp)));
  const avgRain = Math.round(allDaily.reduce((a, d) => a + d.rain_prob, 0) / allDaily.length);
  let s = `未來幾天 ${cityName} 山區露營地氣溫約 ${minT}–${maxT}°C`;
  if (avgRain < 30) s += ',整體降雨機率偏低,適合出遊。';
  else if (avgRain < 60) s += `,平均降雨機率約 ${avgRain}%,建議備雨具。`;
  else s += `,平均降雨機率偏高(約 ${avgRain}%),請留意天氣變化。`;
  return s;
}

// ------------------------------------------------------------------
// 5. 距離 / 最近城市市區 (Haversine,真實座標)
// ------------------------------------------------------------------
export function deg2rad(deg: number): number {
  return deg * (Math.PI / 180);
}

export function getDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// 各縣市「市區/縣治」中心座標 (真實地理資料)
const CITY_CENTERS: Record<string, { lat: number; lng: number; name: string }> = {
  基隆市: { lat: 25.1276, lng: 121.7392, name: '基隆市區' },
  台北市: { lat: 25.0478, lng: 121.5170, name: '台北車站' },
  新北市: { lat: 25.0126, lng: 121.4657, name: '板橋' },
  桃園市: { lat: 24.9937, lng: 121.3010, name: '桃園市區' },
  新竹市: { lat: 24.8039, lng: 120.9686, name: '新竹市區' },
  新竹縣: { lat: 24.8271, lng: 121.0177, name: '竹北' },
  苗栗縣: { lat: 24.5602, lng: 120.8214, name: '苗栗市區' },
  台中市: { lat: 24.1369, lng: 120.6869, name: '台中車站' },
  彰化縣: { lat: 24.0756, lng: 120.5387, name: '彰化市區' },
  南投縣: { lat: 23.9099, lng: 120.6853, name: '南投市區' },
  雲林縣: { lat: 23.7075, lng: 120.5439, name: '斗六' },
  嘉義市: { lat: 23.4801, lng: 120.4491, name: '嘉義市區' },
  嘉義縣: { lat: 23.4518, lng: 120.2555, name: '太保' },
  台南市: { lat: 22.9971, lng: 120.2129, name: '台南車站' },
  高雄市: { lat: 22.6393, lng: 120.3020, name: '高雄車站' },
  屏東縣: { lat: 22.6761, lng: 120.4942, name: '屏東市區' },
  宜蘭縣: { lat: 24.7570, lng: 121.7533, name: '宜蘭市區' },
  花蓮縣: { lat: 23.9769, lng: 121.6044, name: '花蓮市區' },
  台東縣: { lat: 22.7583, lng: 121.1444, name: '台東市區' },
  澎湖縣: { lat: 23.5711, lng: 119.5793, name: '馬公' },
  金門縣: { lat: 24.4321, lng: 118.3171, name: '金城' },
  連江縣: { lat: 26.1608, lng: 119.9512, name: '南竿' },
};

// 距所在縣市市區的直線距離(km);無座標則 null
export function getDistanceToCityCenter(camp: Camp): { km: number; centerName: string } | null {
  if (!camp.lat || !camp.lng) return null;
  const center = CITY_CENTERS[camp.city];
  if (!center) return null;
  const km = getDistanceKm(camp.lat, camp.lng, center.lat, center.lng);
  return { km: Math.round(km), centerName: center.name };
}

// ------------------------------------------------------------------
// 6. 薄頁安全網 (T5.4) — 保守判定,主要防「未來」加入的薄資料。
//    目前資料 desc 皆 ≥78 字、tags ≥2,所以正常營區一律回 false。
// ------------------------------------------------------------------
export function isThinCamp(camp: Camp): boolean {
  const descLen = (camp.description ?? '').trim().length;
  const tagCount = (camp.tags ?? []).length;
  const hasGeo = !!(camp.lat && camp.lng);
  return descLen < 40 || tagCount < 2 || !hasGeo;
}
