export const ads = [
  {
    id: 'gear-upgrade',
    badges: [
      { text: '⚡ 限時優惠', color: 'amber' },
      { text: '裝備升級', color: 'emerald' }
    ],
    title: '還在煩惱缺什麼裝備嗎？',
    desc: '工欲善其事，必先利其器。看看資深露友們都在用什麼好物，讓露營體驗更舒適。',
    image: '/gear.webp',
    cta: '前往 momo 購物網逛逛',
    link: 'https://www.momoshop.com.tw/category/LgrpCategory.jsp?l_code=1699900000'
  },
  {
    id: 'glamping-trip',
    badges: [
      { text: '✨ 豪華體驗', color: 'purple' },
      { text: '免裝備', color: 'pink' }
    ],
    title: '想露營又不想搭帳棚？',
    desc: '精選全台豪華露營 Glamping！冷氣、獨立衛浴、星空電影院，輕鬆享受大自然。',
    image: '/glamping.webp',
    cta: '查看 Klook 優惠行程',
    link: 'https://www.klook.com/zh-TW/search/result/?query=%E8%B1%AA%E8%8F%AF%E9%9C%B2%E7%87%9F'
  },
  {
    id: 'camp-food',
    badges: [
      { text: '🔥 野炊美食', color: 'orange' },
      { text: '大廚上菜', color: 'red' }
    ],
    title: '露營吃什麼？美味輕鬆煮',
    desc: '戶外料理神隊友！從鑄鐵鍋到方便調理包，無需繁瑣準備，野外也能端出五星級料理。',
    image: '/food.webp',
    cta: '逛逛 momo 露營食材',
    link: 'https://www.momoshop.com.tw/search/searchShop.jsp?keyword=%E9%9C%B2%E7%87%9F%E9%A3%9F%E6%9D%90'
  },
  {
    id: 'summer-cool',
    badges: [
      { text: '❄️ 涼感推薦', color: 'blue' },
      { text: '消暑必備', color: 'cyan' }
    ],
    title: '拒絕悶熱！夏日露營攻略',
    desc: '移動式冷氣、大風量循環扇、保冰桶。帶對裝備，夏天露營也能涼爽舒適。',
    image: '/summer.webp',
    cta: '前往 momo 抗熱專區',
    link: 'https://www.momoshop.com.tw/search/searchShop.jsp?keyword=%E9%9C%B2%E7%87%9F%E9%A2%A8%E6%89%87'
  }
];

// Helper function to map color names to Tailwind classes
export function getBadgeClasses(color: string) {
    // 這裡列舉出所有可能用到的顏色，確保 Tailwind 編譯時不會遺漏
    const colors: Record<string, string> = {
        amber: 'text-amber-600 bg-amber-50 border-amber-100',
        emerald: 'text-emerald-600 bg-emerald-50 border-emerald-100',
        purple: 'text-purple-600 bg-purple-50 border-purple-100',
        pink: 'text-pink-600 bg-pink-50 border-pink-100',
        orange: 'text-orange-600 bg-orange-50 border-orange-100',
        red: 'text-red-600 bg-red-50 border-red-100',
        blue: 'text-blue-600 bg-blue-50 border-blue-100',
        cyan: 'text-cyan-600 bg-cyan-50 border-cyan-100',
    };
    return colors[color] || colors['emerald'];
}
