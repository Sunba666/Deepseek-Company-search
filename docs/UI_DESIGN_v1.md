# UI 设计规范 — JobNav AI
> 版本：v1.0
> 状态：初稿
> 设计风格：Linear + Vercel + OpenAI + Apple + Notion 融合
> 框架映射：React + Next.js + TailwindCSS + shadcn/ui + Framer Motion

---

## 一、Design Tokens（设计令牌）

### 1.1 Color System — Light Mode

```css
:root {
  /* Primary */
  --color-primary-50:  #EEF2FF;
  --color-primary-100: #E0E7FF;
  --color-primary-200: #C7D2FE;
  --color-primary-300: #A5B4FC;
  --color-primary-400: #818CF8;
  --color-primary-500: #6366F1;    /* Main primary */
  --color-primary-600: #4F46E5;
  --color-primary-700: #4338CA;
  --color-primary-800: #3730A3;
  --color-primary-900: #312E81;

  /* Neutral / Gray */
  --color-gray-50:   #F9FAFB;
  --color-gray-100:  #F3F4F6;
  --color-gray-200:  #E5E7EB;
  --color-gray-300:  #D1D5DB;
  --color-gray-400:  #9CA3AF;
  --color-gray-500:  #6B7280;
  --color-gray-600:  #4B5563;
  --color-gray-700:  #374151;
  --color-gray-800:  #1F2937;
  --color-gray-900:  #111827;

  /* Semantic Colors */
  --color-success:   #10B981;
  --color-warning:   #F59E0B;
  --color-error:     #EF4444;
  --color-info:      #3B82F6;

  /* Surface & Background */
  --bg-primary:      #FFFFFF;
  --bg-secondary:    #F9FAFB;
  --bg-tertiary:     #F3F4F6;

  /* Text */
  --text-primary:    #111827;
  --text-secondary:  #6B7280;
  --text-disabled:   #9CA3AF;
  --text-inverse:    #FFFFFF;

  /* Border */
  --border-default:  #E5E7EB;
  --border-hover:    #D1D5DB;
  --border-focused:  #6366F1;

  /* Shadow */
  --shadow-xs:  0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm:  0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md:  0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
  --shadow-lg:  0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
  --shadow-xl:  0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
  --shadow-card: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-popup: 0 10px 25px rgba(0,0,0,0.12), 0 4px 10px rgba(0,0,0,0.08);
}
```

### 1.2 Color System — Dark Mode

```css
.dark {
  --color-primary-50:  #E0E7FF;
  --color-primary-100: #C7D2FE;
  --color-primary-200: #A5B4FC;
  --color-primary-300: #818CF8;
  --color-primary-400: #6366F1;
  --color-primary-500: #4F46E5;
  --color-primary-600: #4338CA;
  --color-primary-700: #3730A3;
  --color-primary-800: #312E81;
  --color-primary-900: #1E1B4B;

  --color-gray-50:   #F9FAFB;
  --color-gray-100:  #F3F4F6;
  --color-gray-200:  #E5E7EB;
  --color-gray-300:  #D1D5DB;
  --color-gray-400:  #9CA3AF;
  --color-gray-500:  #6B7280;
  --color-gray-600:  #4B5563;
  --color-gray-700:  #374151;
  --color-gray-800:  #1F2937;
  --color-gray-900:  #111827;

  /* Dark mode overrides */
  --bg-primary:      #0F1117;
  --bg-secondary:    #1A1D28;
  --bg-tertiary:     #232734;
  --text-primary:    #EDEDEE;
  --text-secondary:  #9B9CA4;
  --text-disabled:   #6B6C74;
  --text-inverse:    #0F1117;
  --border-default:  #2E303E;
  --border-hover:    #3E4050;
  --border-focused:  #6366F1;
}
```

### 1.3 Typography

```css
:root {
  /* Font Family */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Sizes & Line Heights */
  --text-h1:       32px/40px   700  -0.02em;
  --text-h2:       24px/32px   600  -0.01em;
  --text-h3:       20px/28px   600  -0.01em;
  --text-h4:       18px/26px   600  0;
  --text-title:    16px/24px   600  0;
  --text-subtitle: 14px/22px   500  0;
  --text-body-lg:  16px/26px   400  0;
  --text-body:     14px/22px   400  0;
  --text-caption:  12px/18px   400  0.01em;
  --text-button:   14px/20px   500  0.01em;
  --text-tag:      11px/16px   500  0.02em;
}
```

### 1.4 Spacing (8pt Grid)

```css
:root {
  --space-1: 4px;    /* 4px  */
  --space-2: 8px;    /* 8px  */
  --space-3: 12px;   /* 12px */
  --space-4: 16px;   /* 16px */
  --space-5: 20px;   /* 20px */
  --space-6: 24px;   /* 24px */
  --space-8: 32px;   /* 32px */
  --space-10: 40px;  /* 40px */
  --space-12: 48px;  /* 48px */
  --space-16: 64px;  /* 64px */
  --space-20: 80px;  /* 80px */
  --space-24: 96px;  /* 96px */
}
```

### 1.5 Border Radius

```css
:root {
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 20px;
  --radius-3xl: 24px;
  --radius-full: 9999px;
}
```

### 1.6 Shadows

```css
:root {
  /* Card — subtle, for cards and panels */
  --shadow-card: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  /* Hover — elevated on hover */
  --shadow-hover: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
  /* Popup — for dropdowns, tooltips */
  --shadow-popup: 0 10px 25px rgba(0,0,0,0.12), 0 4px 10px rgba(0,0,0,0.08);
  /* Dialog — for modals, dialogs */
  --shadow-dialog: 0 20px 40px rgba(0,0,0,0.15), 0 8px 20px rgba(0,0,0,0.1);
  /* Dropdown — for command palette, large menus */
  --shadow-dropdown: 0 25px 50px rgba(0,0,0,0.2), 0 8px 20px rgba(0,0,0,0.08);
}

/* Dark mode shadows use lower opacity black + color overlay */
.dark {
  --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.4);
  --shadow-popup: 0 10px 25px rgba(0,0,0,0.5);
  --shadow-dialog: 0 20px 40px rgba(0,0,0,0.6);
  --shadow-dropdown: 0 25px 50px rgba(0,0,0,0.7);
}
```

### 1.7 Animation Tokens

```css
:root {
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* Framer Motion variants */
  --fade-in: { opacity: 0 -> 1, duration: 0.2 };
  --slide-up: { y: 20 -> 0, opacity: 0 -> 1, duration: 0.3 };
  --scale-in: { scale: 0.95 -> 1, opacity: 0 -> 1, duration: 0.2 };
}
```

---

## 二、Component Library（组件库）

### 2.1 Button

| Variant | Light | Dark | Usage |
|---------|-------|------|-------|
| Primary | bg-primary-500 text-white | same | CTA, 主要操作 |
| Secondary | bg-gray-100 text-gray-900 | bg-gray-800 text-gray-100 | 次要操作 |
| Outline | border border-gray-300 text-gray-700 | border-gray-600 text-gray-300 | 辅助操作 |
| Ghost | text-gray-700 hover:bg-gray-100 | text-gray-300 hover:bg-gray-800 | 轻量操作 |
| Link | text-primary-500 underline | same | 文本跳转 |
| Danger | bg-red-500 text-white | same | 危险操作 |
| Icon | 40x40 rounded-md | same | 图标按钮 |
| FAB | 56px rounded-full shadow-lg | same | AI Copilot 浮动按钮 |

Implementation mapping: `shadcn/ui Button` with custom variants via `cva()`

```tsx
// Button component tokens
<Button variant="primary" size="md" loading={isLoading}>
  {children}
</Button>
// size: sm(32px) / md(40px) / lg(48px)
// variant: primary / secondary / outline / ghost / danger / link
```

### 2.2 Input & Form

| Component | shadcn/ui mapping | Customization |
|-----------|-------------------|---------------|
| Input | Input | Rounded-md, focus-ring, error state |
| Textarea | Textarea | Resize: vertical, min-h: 100px |
| Search | Input + SearchIcon | With clear button, hotkey "/" |
| Select | Select | Custom chevron, searchable |
| MultiSelect | Command + Badge | Tag-style selection |
| Checkbox | Checkbox | Custom check animation |
| Radio | RadioGroup | Custom circle animation |
| Switch | Switch | Smooth toggle animation |
| DatePicker | Popover + Calendar | Range selection |
| Upload | File Input + DragZone | Drag & drop, preview |
| Slider | Slider | Dual thumb for range |
| Rating | Star icons | Clickable rating 1-5 |

### 2.3 Navigation

| Component | shadcn/ui mapping | Description |
|-----------|-------------------|-------------|
| Navbar | Custom | Fixed top, glassmorphism, 64px height |
| Sidebar | Sheet | Desktop: permanent, Mobile: overlay |
| Breadcrumb | Breadcrumb | Auto-generated from route |
| Tabs | Tabs | Underline style, animated indicator |
| Pagination | Pagination | Show page numbers + prev/next |
| DropdownMenu | DropdownMenu | With icons, separator, disabled |
| Drawer | Sheet | Right drawer for filters |
| CommandPalette | Command | Cmd+K, global search |

### 2.4 Feedback

| Component | shadcn/ui mapping | Description |
|-----------|-------------------|-------------|
| Toast | Toast | Top-right, auto-dismiss, stacked |
| Snackbar | Sonner | Bottom-center, action button |
| Modal | Dialog | Centered, ESC to close, backdrop blur |
| Dialog | AlertDialog | Confirm/cancel actions |
| Tooltip | Tooltip | Top by default, delay 500ms |
| Popover | Popover | Click to open, click outside to close |
| Skeleton | Skeleton | Pulse animation, matching layout |
| Progress | Progress | Linear, percentage, animated |
| Loading | Spinner | 20px, primary color |

### 2.5 Data Display

| Component | shadcn/ui mapping | Description |
|-----------|-------------------|-------------|
| Table | Table | Striped rows, sortable headers |
| Card | Card | Border + shadow, hover elevation |
| Badge | Badge | Status/Count/Tag variants |
| Avatar | Avatar | Image with fallback initials |
| Statistic | Custom | Number + label + trend arrow |
| Empty | Custom | Illustration + message + CTA |
| Tag | Badge variant="outline" | Skill tags, clickable |
| Timeline | Custom | Vertical timeline with dots |

### 2.6 Card Components

```
CompanyCard : Card
  - Logo (48x48)
  - Name + Industry
  - Hiring count badge
  - City + Stage tags
  - Action: View details

JobCard : Card
  - Title + Company name
  - Salary range (highlighted)
  - City + Experience + Education tags
  - Skill tags (max 5, +more)
  - Referral count
  - Match score badge (when applicable)
  - Actions: Save / Apply / Share

ReferralCard : Card
  - Referral code (monospace, highlighted)
  - Confidence score (color-coded)
  - Referrer name + company
  - Published time
  - Verification status badge
  - Actions: Copy code / Go to link

InterviewCard : Card
  - Company name + Job title
  - Difficulty badge
  - Rounds count
  - Result badge (Offer/Rejected)
  - Key topics (tags)
  - Action: Read full

AICard : Card
  - AI icon + Title
  - Score/Progress (if applicable)
  - Key insights (3 lines)
  - Action: View analysis

DashboardCard : Card
  - Icon + Label
  - Value (large number)
  - Trend (up/down) + percentage
  - Sparkline chart
```

---

## 三、Layout System（布局系统）

### 3.1 Grid System

```
12 Column Grid
Desktop (1280px+): 12 columns, gap 24px, max-width 1280px
Tablet (768-1279px): 8 columns, gap 20px
Mobile (<768px): 4 columns, gap 16px

Page padding:
  Desktop: 32px (sides), 24px (top/bottom)
  Tablet: 24px
  Mobile: 16px

Content width:
  Max: 1280px
  Narrow: 768px (for detail pages)
```

### 3.2 Page Shell

```
+--------------------------------------------------+
|  TopNav (64px)                                    |
|  [Logo] [Nav Links] [Search] [Theme] [User Menu]  |
+--------------------------------------------------+
|                                                    |
|  Page Content (min-height: calc(100vh - 64px))     |
|                                                    |
|  +-- Breadcrumb (optional) ---------------------+  |
|  |  Home > Jobs > Job Detail                     |  |
|  +----------------------------------------------+  |
|                                                    |
|  +-- Main Content -----------------------------+  |
|  |  [Content area with 12-column grid]          |  |
|  |                                               |  |
|  +----------------------------------------------+  |
|                                                    |
+--------------------------------------------------+
|  Footer (optional)                                 |
+--------------------------------------------------+

--- Floating Elements ---
  AI Copilot FAB (fixed bottom-right, 56px)
  Back to Top (fixed bottom-right, appears on scroll)
```

---

## 四、页面设计

### 4.1 首页 (Home)

```
+------------------------------------------------------------------+
|  Navbar [Logo] [公司] [岗位] [内推] [AI推荐] [🔍搜索...] [🌙] [👤] |
+------------------------------------------------------------------+
|                                                                    |
|  ┌─────────────── Hero Section ──────────────────────────────┐    |
|  │                                                           │    |
|  │  发现你的理想工作                                          │    |
|  │  AI 驱动的智能求职导航 · 内推聚合 · 官网直达               │    |
|  │                                                           │    |
|  │  ┌─────────────────────────────────────────────────────┐  │    |
|  │  │ 🔍 搜索岗位、公司、技能...                    [AI搜索] │  │    |
|  │  └─────────────────────────────────────────────────────┘  │    |
|  │                                                           │    |
|  │  热门: AI算法工程师 · Java后端 · 产品经理 · 前端开发 · UX设计 │    |
|  └───────────────────────────────────────────────────────────┘    |
|                                                                    |
|  ┌─── AI Daily Opportunities ────────────────────────────────┐    |
|  │ 📰 今日新增 156 个岗位                                    │    |
|  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │    |
|  │  │字节跳动  │ │ 腾讯    │ │ 阿里巴巴 │ │ OpenAI  │        │    |
|  │  │ 31个岗位 │ │ 12个岗位│ │ 18个岗位 │ │ 5个岗位 │        │    |
|  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │    |
|  └───────────────────────────────────────────────────────────┘    |
|                                                                    |
|  ┌─── AI 推荐岗位 ────────────────────────────────────────────┐  |
|  │ 🤖 根据你的简历推荐                                       │  |
|  │ ┌─ JobCard ──────────┐ ┌─ JobCard ──────────┐             │  |
|  │ │ AI算法工程师       │ │ Java后端开发       │             │  |
|  │ │ 字节跳动 · 上海    │ │ 腾讯 · 深圳        │             │  |
|  │ │ 50K-80K ▸ 92% 匹配 │ │ 30K-60K ▸ 85% 匹配 │             │  |
|  │ │ Python PyTorch 大模型│ │ Java Spring MySQL  │             │  |
|  │ │ 🎯 内推 5个  ⭐收藏  │ │ 🎯 内推 3个  ⭐收藏  │             │  |
|  │ └─────────────────────┘ └─────────────────────┘             │  |
|  └───────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌─── 热门公司 ────────────────────────────────────────────────┐ |
|  │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐         │ |
|  │ │字节  │ │ 腾讯 │ │ 阿里 │ │ 美团 │ │ 京东 │ │ 拼多多│        │ |
|  │ │跳动  │ │      │ │ 巴巴 │ │      │ │      │ │       │        │ |
|  │ │128岗 │ │ 95岗 │ │ 82岗 │ │ 45岗 │ │ 38岗 │ │ 35岗  │        │ |
|  │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘         │ |
|  └───────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌─── 最新内推 ────────────────────────────────────────────────┐ |
|  │ ┌─ ReferralCard ─────────────────────────┐                  │ |
|  │ │ 🎯 NTABkC8         可信度 95/100 ★★★★★ │                  │ |
|  │ │ 字节跳动 · Java后端 · 张三(员工认证)    │                  │ |
|  │ │ ⏱ 3天前发布  ✅ 已验证  [复制] [投递]    │                  │ |
|  │ └──────────────────────────────────────────┘                  │ |
|  └───────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌─── 热门城市 & 技能 ──────────────────────────────────────────┐|
|  │ 城市: 北京🔥 上海🔥 深圳🔥 杭州🔥 广州🔥 成都🔥 Remote🔥     │|
|  │ 技能: AI算法🔥 Java🔥 前端🔥 Python🔥 大模型🔥 Agent🔥       │|
|  └───────────────────────────────────────────────────────────┘|
|                                                                    |
+------------------------------------------------------------------+
|  Footer [关于] [反馈] [隐私] [条款] © 2024 JobNav AI             |
+------------------------------------------------------------------+
```

### 4.2 岗位搜索页 (Jobs)

```
+------------------------------------------------------------------+
|  Navbar                                                   |
+------------------------------------------------------------------+
|                                                                    |
|  ┌── 筛选面板 ───────────────────────────────────────────────┐  |
|  │                                                            │  |
|  │  🔍 搜索岗位、公司、关键词...                      [AI搜索] │  |
|  │                                                            │  |
|  │  分类: [全部 ▼]  城市: [上海 ▼]  经验: [3-5年 ▼]          │  |
|  │  学历: [本科 ▼]  薪资: [===30K==========80K===]            │  |
|  │                                                            │  |
|  │  更多筛选: [公司规模 ▼] [融资阶段 ▼] [Remote] [外企]      │  |
|  │                                                            │  |
|  │  热门标签: #AI算法 #Java后端 #前端开发 #产品经理 #大数据    │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌── 结果栏 ──────────────────────────────────────────────────┐ |
|  │  共 128 个岗位  视图: [☰列表] [▦卡片]  排序: [最新发布 ▼]  │ |
|  │                                                            │ |
|  │ ┌─ JobCard ──────────────────────────────────────────────┐ │ |
|  │ │ AI算法工程师                              字节跳动      │ │ |
|  │ │ 上海 · 50K-80K · 3-5年 · 硕士            匹配度 92% 🔥 │ │ |
|  │ │ Python PyTorch Transformer 大模型                      │ │ |
|  │ │ 🎯 内推 5个 · 📅 3天前发布 · 🏢 2000+人               │ │ |
|  │ │ ⭐收藏  🔗分享  📋投递管理                            │ │ |
|  │ └───────────────────────────────────────────────────────┘ │ |
|  │ ┌─ JobCard ──────────────────────────────────────────────┐ │ |
|  │ │ Java后端开发工程师                       腾讯           │ │ |
|  │ │ 深圳 · 30K-60K · 3-5年 · 本科           匹配度 85%     │ │ |
|  │ │ Java Spring Boot MySQL Redis                           │ │ |
|  │ │ 🎯 内推 3个 · 📅 1天前发布 · 🏢 2000+人               │ │ |
|  │ │ ⭐收藏  🔗分享  📋投递管理                            │ │ |
|  │ └───────────────────────────────────────────────────────┘ │ |
|  │ ...                                                       │ |
|  │ [< 1 2 3 ... 7 >]                                        │ |
|  └──────────────────────────────────────────────────────────┘ |
|                                                                    |
+------------------------------------------------------------------+
```

### 4.3 岗位详情页 (Job Detail)

```
+------------------------------------------------------------------+
|  Navbar                                                   |
+------------------------------------------------------------------+
|  ← 返回搜索结果                                                    |
|                                                                    |
|  ┌── Header ─────────────────────────────────────────────────┐    |
|  │  AI算法工程师                               字节跳动       │    |
|  │  ⭐ 收藏  🔗 分享  📋 投递管理  🚩 举报                   │    |
|  │                                                            │    |
|  │  ┌────────┬────────┬────────┬────────┬────────┐           │    |
|  │  │ 上海   │ 50-80K │ 3-5年  │ 硕士   │ 92%匹配 │           │    |
|  │  │ 城市   │ 薪资   │ 经验   │ 学历   │ AI匹配   │           │    |
|  │  └────────┴────────┴────────┴────────┴────────┘           │    |
|  └────────────────────────────────────────────────────────────┘    |
|                                                                    |
|  ┌── Content Tabs ────────────────────────────────────────────┐  |
|  │ [📄 职位描述] [🤖 AI分析] [🎯 内推] [💰 薪资] [📝 面经]    │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌── AI 分析 Tab (默认展开) ──────────────────────────────────┐ |
|  │ 🤖 AI JD 分析                                              │ |
|  │                                                            │ |
|  │  匹配度 92% · 非常匹配                                      │ |
|  │  ━━━━━━━━━━━━━━━━━━━━ 92%                                  │ |
|  │                                                            │ |
|  │  ✅ 已具备技能                                              │ |
|  │  #Python #PyTorch #Transformer #LLM #NLP                    │ |
|  │                                                            │ |
|  │  ⚠️ 缺失技能                                               │ |
|  │  · 推荐系统经验 → 学习建议: Andrew Ng 推荐系统课程          │ |
|  │  · 分布式训练 → 学习建议: DeepSpeed 官方文档                │ |
|  │                                                            │ |
|  │  📝 简历优化建议                                           │ |
|  │  · 突出大模型落地项目经验，最好有量化指标                    │ |
|  │  · 补充推荐系统相关项目经验                                 │ |
|  │  · 使用 STAR 法则重构项目描述                               │ |
|  │                                                            │ |
|  │  💰 薪资分析                                               │ |
|  │  市场平均: 45K  市场范围: 30K-70K  您预估: 40K-55K         │ |
|  │                                                            │ |
|  │  [📄 上传简历匹配]  [💬 AI Copilot 咨询]                   │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌── 内推码 ──────────────────────────────────────────────────┐ |
|  │ 🎯 内推码  (共 5 个)                                       │ |
|  │                                                            │ |
|  │ ┌────────────────────────────────────────────────────────┐ │ |
|  │ │ 内推码: NTABkC8         可信度 95/100 ★★★★★ 高可信     │ │ |
|  │ │ 内推人: 张三 · 字节跳动高级工程师 · 已员工认证          │ │ |
|  │ │ ⏱ 3天前发布 · ✅ 已验证 (5人验证)                      │ │ |
|  │ │ [📋 复制内推码]  [🚀 跳转官网投递 →]                   │ │ |
|  │ └────────────────────────────────────────────────────────┘ │ |
|  │ ┌────────────────────────────────────────────────────────┐ │ |
|  │ │ 内推码: ABC123         可信度 60/100 ★★★ 中等          │ │ |
|  │ │ 内推人: 李四 · 未认证                                  │ │ |
|  │ │ ⏱ 10天前发布 · ⚠️ 待验证                              │ │ |
|  │ │ [📋 复制内推码]  [🚀 跳转官网投递 →]                   │ │ |
|  │ └────────────────────────────────────────────────────────┘ │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌── 职位时间轴 ──────────────────────────────────────────────┐ |
|  │ ⏱ 职位状态                                                │ |
|  │ ● 发布 01-15  ● 更新 01-20  ● 内推 5个  ● 截止 02-29      │ |
|  │ ● 状态: 招聘中                                             │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌── 推荐岗位 ────────────────────────────────────────────────┐ |
|  │ 📋 相似岗位推荐                                            │ |
|  │ ┌──────┐ ┌──────┐ ┌──────┐                               │ |
|  │ │NLP算法│ │CV算法│ │推荐算│                               │ |
|  │ │ 工程师│ │ 工程师│ │ 法   │                               │ |
|  │ │ 字节  │ │ 腾讯  │ │ 美团 │                               │ |
|  │ └──────┘ └──────┘ └──────┘                               │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
+------------------------------------------------------------------+
```

### 4.4 AI Copilot 对话界面

```
+------------------------------------------------------------------+
|                    AI 求职 Copilot                                 |
+------------------------------------------------------------------+
|  ┌────────────┐  ┌─────────────────────────────┐  ┌──────────┐  |
|  │ 对话历史    │  │  AI 助手                    │  │ 推荐内容  │  |
|  │            │  │                             │  │          │  |
|  │ 今天       │  │ 你好！我是 JobNav AI         │  │ 推荐岗位  │  |
|  │  ├ 上海AI  │  │ 求职助手，可以帮你：         │  │ ┌──────┐ │  |
|  │  ├ 字节推   │  │                             │  │ │AI算法│ │  |
|  │  ├ JD分析  │  │ ▸ 推荐岗位「推荐上海AI产品」 │  │ │ 工程师│ │  |
|  │            │  │ ▸ 分析JD「帮我分析这个岗位」  │  │ │ 92%  │ │  |
|  │ 上周       │  │ ▸ 公司内推「我想进字节跳动」  │  │ └──────┘ │  |
|  │  ├ 简历优化 │  │ ▸ 简历优化「帮我优化简历」   │  │ ┌──────┐ │  |
|  │            │  │                             │  │ │Java后│ │  |
|  │ [新建对话] │  │ ──────────────────────────── │  │ │  端  │ │  |
|  │            │  │                             │  │ │ 85%  │ │  |
|  │            │  │ 🧑 推荐上海AI产品经理岗位     │  │ └──────┘ │  |
|  │            │  │                             │  │          │  |
|  │            │  │ 🤖 好的！为您找到 8 个       │  │ 推荐公司  │  |
|  │            │  │ 上海 AI 产品经理岗位...      │  │ 字节跳动  │  |
|  │            │  │                             │  │ 腾讯     │  |
|  │            │  │ ┌─ 结果 ─────────────────┐ │  │ 阿里巴巴  │  |
|  │            │  │ │ AI产品经理 · 字节跳动   │ │  │          │  |
|  │            │  │ │ 上海 · 40K-70K · 85%   │ │  │ 快捷操作  │  |
|  │            │  │ │ [查看详情] [投递]       │ │  │ 📄上传简历│  |
|  │            │  │ └────────────────────────┘ │  │ 🔍分析JD  │  |
|  │            │  │ ┌─ ... ──────────────────┐ │  │ 🎯推荐岗位│  |
|  │            │  │ │ ...                    │ │  │ 🎤模拟面试│  |
|  │            │  │ └────────────────────────┘ │  │ 📊Offer比 │  |
|  │            │  │                             │  │           │  |
|  │            │  │ ──────────────────────────── │  │           │  |
|  │            │  │                              │  │           │  |
|  │            │  │ [输入消息...]          [发送] │  │           │  |
|  │            │  │                              │  │           │  |
|  └────────────┘  └─────────────────────────────┘  └──────────┘  |
+------------------------------------------------------------------+
```

### 4.5 投递管理 Dashboard (CRM)

```
+------------------------------------------------------------------+
|  📋 投递管理                                                      |
|  [看板视图]  [列表视图]  [统计视图]                                |
+------------------------------------------------------------------+
|  ┌── Stats Bar ──────────────────────────────────────────────┐  |
|  │  📊 总投递: 12  📩 回复率: 58%  🎙️ 面试率: 42%           │  |
|  │  ✅ Offer率: 25%  ⏱ 平均响应: 5天  📈 本月新增: 3        │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌── Kanban Board ────────────────────────────────────────────┐ |
|  │ ┌─Saved─┐ ┌─Ready─┐ ┌─Applied─┐ ┌─HR Seen─┐ ┌─Written─┐  │ |
|  │ │       │ │       │ │         │ │         │ │         │  │ |
|  │ │阿里PM │ │腾讯   │ │ 字节    │ │ 美团    │ │         │  │ |
|  │ │收藏   │ │准备   │ │ 已投递  │ │ HR查看  │ │         │  │ |
|  │ │01-15  │ │01-18  │ │ 01-20   │ │ 01-22   │ │         │  │ |
|  │ │       │ │       │ │ NTABkC8 │ │         │ │         │  │ |
|  │ │       │ │       │ │         │ │         │ │         │  │ |
|  │ │拼多多 │ │       │ │ 小红书  │ │         │ │         │  │ |
|  │ ├───────┤ ├───────┤ ├─────────┤ ├─────────┤ ├─────────┤  │ |
|  │ │ + 添加 │ │ + 添加 │ │ + 添加  │ │ + 添加  │ │ + 添加  │  │ |
|  │ └───────┘ └───────┘ └─────────┘ └─────────┘ └─────────┘  │ |
|  │ ┌Interview1┐ ┌Interview2┐ ┌HRInterview┐ ┌─Offer──┐ ┌Rejected┐ │ |
|  │ │ 拼多多   │ │          │ │           │ │腾讯   │ │        │ │ |
|  │ │ 前端     │ │          │ │           │ │Java   │ │字节    │ │ |
|  │ │ 一面     │ │          │ │           │ │Offer! │ │算法    │ │ |
|  │ └──────────┘ └──────────┘ └───────────┘ └────────┘ └────────┘ │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
|  ┌── AI 建议 ─────────────────────────────────────────────────┐  |
|  │ 💡 您当前面试率 42%，高于平均水平。建议：                    │  |
|  │ · 关注「字节跳动 AI 算法工程师」岗位，匹配度 92%            │  |
|  │ · 您收藏的「小红书」岗位已发布新内推码                      │  |
|  │ · 腾讯 Offer 薪资高于市场 P75，建议优先考虑                 │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
+------------------------------------------------------------------+
```

### 4.6 公司详情页

```
+------------------------------------------------------------------+
|  ← 返回公司列表                                                    |
+------------------------------------------------------------------+
|  ┌── Company Header ────────────────────────────────────────┐    |
|  │  [Logo] 字节跳动  · 互联网 · 2000+人 · 独角兽            │    |
|  │  ⭐ 关注公司  🔗 官网  📋 全部岗位                       │    |
|  └──────────────────────────────────────────────────────────┘    |
|                                                                    |
|  ┌── AI 公司画像 ────────────────────────────────────────────┐  |
|  │ 🤖 AI 综合分析                                             │  |
|  │                                                            │  |
|  │  综合评分 8.5/10                                           │  |
|  │  ━━━━━━━━━━━━━━━ 85%                                       │  |
|  │                                                            │  |
|  │  薪资 8.0  ████████░░                                     │  |
|  │  文化 7.5  ███████░░░                                     │  |
|  │  成长 9.0  █████████░                                     │  |
|  │  稳定 7.0  ███████░░░                                     │  |
|  │                                                            │  |
|  │  招聘趋势: 📈 增长中  热度: 85/100                         │  |
|  │  内推活跃度: 🔥 高 (15个有效内推)                          │  |
|  │  面试难度: ⭐⭐⭐⭐ (困难) 平均 4 轮                       │  |
|  │                                                            │  |
|  │  ✅ 优点: 薪资高 · 成长快 · 技术氛围好 · 福利完善          │  |
|  │  ⚠️ 缺点: 加班多 · 竞争激烈 · 业务调整频繁                 │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌── Tabs ───────────────────────────────────────────────────┐  |
|  │ [📋 全部岗位] [🎯 内推] [💰 薪资] [📝 面经] [📰 公司动态] │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌── 在招岗位 (128个) ───────────────────────────────────────┐ |
|  │  筛选: [全部 ▼]  [上海 ▼]                                  │ |
|  │ ┌─ JobCard ──────────────┐ ┌─ JobCard ──────────────┐     │ |
|  │ │ AI算法工程师           │ │ Java后端开发           │     │ |
|  │ │ 上海 · 50K-80K         │ │ 深圳 · 30K-60K         │     │ |
|  │ │ 🎯内推5个              │ │ 🎯内推3个              │     │ |
|  │ └────────────────────────┘ └────────────────────────┘     │ |
|  └────────────────────────────────────────────────────────────┘ |
|                                                                    |
+------------------------------------------------------------------+
```

### 4.7 管理后台 — Dashboard

```
+------------------------------------------------------------------+
|  [Logo]  Admin Panel  [🔍搜索]  [🔔]  [👤管理员]                |
+------------------------------------------------------------------+
|  ┌──────┐  ┌── Main Content ───────────────────────────────┐    |
|  │ Side  │  │ 📊 数据概览                                     │    |
|  │ bar   │  │                                                  │    |
|  │       │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐  │  |
|  │ 📊    │  │ │ 总用户    │ │ 总岗位    │ │ 总内推    │ │ 投递  │  │  |
|  │ 概览   │  │ │ 12,580   │ │ 5,234    │ │ 892      │ │ 1,245 │  │  |
|  │       │  │ │ 📈+12%    │ │ 📈+8%    │ │ 📈+15%   │ │ 📈+5% │  │  |
|  │ 👥    │  │ └──────────┘ └──────────┘ └──────────┘ └──────┘  │  |
|  │ 用户   │  │                                                  │  |
|  │       │  │ ┌── 图表 ──────────────────────────────────────┐  │  |
|  │ 🏢    │  │ │ 📈 用户增长趋势 (近30天)                      │  │  |
|  │ 公司   │  │ │  ▁▃▆█▇▆▅▆█▇▆▅▄▃▅▆▇█▇▆▅▄▃                  │  │  |
|  │       │  │ └──────────────────────────────────────────────┘  │  |
|  │ 📋    │  │                                                  │  |
|  │ 岗位   │  │ ┌── 最新动态 ──────────────────────────────────┐  │  |
|  │       │  │ │ 🕐 10:23 用户「小明」上传简历                  │  │  |
|  │ 🔗    │  │ │ 🕐 10:15 新岗位「AI算法工程师」待审核          │  │  |
|  │ 内推   │  │ │ 🕐 09:50 内推码「NTABkC8」被举报失效           │  │  |
|  │       │  │ └──────────────────────────────────────────────┘  │  |
|  │ 📝    │  └──────────────────────────────────────────────────┘  |
|  │ 审核   │                                                       |
|  │       │                                                       |
|  │ 🤖    │                                                       |
|  │ AI配置 │                                                       |
|  │       │                                                       |
|  │ 📊    │                                                       |
|  │ 统计   │                                                       |
|  │       │                                                       |
|  │ ⚙️    │                                                       |
|  │ 系统   │                                                       |
|  └──────┘                                                       |
+------------------------------------------------------------------+
```

---

## 五、Animation System（动画系统）

### 5.1 Page Transitions

```tsx
// page.tsx — Next.js App Router page transition
'use client';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

export default function PageLayout({ children }) {
  return (
    <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
      {children}
    </motion.div>
  );
}
```

### 5.2 Component Animations

| Component | Animation | Framer Motion |
|-----------|-----------|---------------|
| Card hover | Scale 1.01 + Shadow | whileHover={{ scale: 1.01, boxShadow: '0 4px 12px ...' }} |
| Modal | Scale in + Fade | initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} |
| Drawer | Slide from right | initial={{ x: '100%' }} animate={{ x: 0 }} |
| Toast | Slide in from top | initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} |
| List item | Stagger fade in | staggerChildren: 0.05, each: { opacity: 0, y: 10 -> 0 } |
| Skeleton | Pulse shimmer | animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity }} |
| Tabs indicator | Animate layout | layoutId="tab-indicator" |
| Button loading | Spin icon | animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }} |
| AI typing | Typewriter effect | Character-by-character reveal |
| Scroll reveal | Fade in on scroll | whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} |

### 5.3 Micro-interactions

```
- Button click: scale 0.97 -> 1 (50ms)
- Link hover: underline expand from center
- Input focus: border color transition + subtle glow
- Star favorite: scale + rotate animation
- Copy referral code: "Copied!" toast + code highlight flash
- Status drag (CRM): smooth drag with drop zone highlight
- AI thinking: 3-dot bounce animation
- Notification dot: pulse animation when new
- Theme switch: smooth background transition (500ms)
```

---

## 六、Responsive Design（响应式方案）

### 6.1 Breakpoints

```css
/* Tailwind breakpoints */
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop small */
xl:  1280px  /* Desktop wide */
2xl: 1536px  /* Desktop ultra-wide */
```

### 6.2 Responsive Layout Rules

| Element | Desktop (1280+) | Tablet (768-1279) | Mobile (<768) |
|---------|:--------------:|:-----------------:|:-------------:|
| Navbar | Full | Full | Compact (hamburger) |
| Sidebar | Visible | Collapsible | Hidden (drawer) |
| Hero | Full width | Full width | Compact |
| Job List | 2 columns | 2 columns | 1 column |
| Detail Page | 3-column | 2-column | 1-column stacked |
| Copilot | 3-column | Sidebar hidden | Full screen popup |
| CRM Kanban | All columns | Scroll horizontal | Stacked list |
| Admin | Sidebar + content | Sidebar collapsed | Drawer navigation |
| Card grid | 4 columns | 3 columns | 2 columns |
| Filters | Inline | Collapsible | Bottom sheet |

### 6.3 Mobile Specific

```
Navigation: Bottom tab bar (5 icons: Home, Jobs, AI, Pipeline, Profile)
Filters: Bottom sheet drawer (slide up)
AI Copilot: Full-screen modal (slide up from bottom)
CRM: List view instead of kanban (swipeable status change)
Jobs: Single column list with swipe-to-save
```

---

## 七、Component Naming Convention

### 7.1 File Structure

```
src/
+-- components/
|   +-- ui/                   # shadcn/ui base components
|   |   +-- button.tsx
|   |   +-- card.tsx
|   |   +-- input.tsx
|   |   +-- ...
|   +-- shared/               # Shared business components
|   |   +-- JobCard.tsx
|   |   +-- CompanyCard.tsx
|   |   +-- ReferralCard.tsx
|   |   +-- ...
|   +-- layout/               # Layout components
|   |   +-- Navbar.tsx
|   |   +-- Footer.tsx
|   |   +-- Sidebar.tsx
|   |   +-- ...
|   +-- ai/                   # AI-specific components
|   |   +-- Copilot.tsx
|   |   +-- JDAnalysis.tsx
|   |   +-- ResumeMatch.tsx
|   +-- pipeline/             # CRM components
|   |   +-- KanbanBoard.tsx
|   |   +-- ApplicationCard.tsx
|   |   +-- StatsPanel.tsx
+-- app/                      # Next.js App Router pages
|   +-- (public)/             # Public routes
|   +-- (auth)/               # Auth routes (login/register)
|   +-- (dashboard)/          # Protected routes
|   +-- admin/                # Admin routes
```

### 7.2 Component Prop Patterns

```tsx
// All components follow this pattern:
interface ComponentProps {
  variant?: 'default' | 'primary' | 'secondary';  // Visual variant
  size?: 'sm' | 'md' | 'lg';                       // Size
  className?: string;                                // Override classes
  children?: React.ReactNode;
  [key: string]: any;                                // Native HTML attrs
}
```

---

## 八、shadcn/ui 组件映射表

| Design Component | shadcn/ui Component | Customization |
|-----------------|--------------------|---------------|
| Button | Button | Custom variants via cva() |
| Input | Input | With icon slot, error state |
| Select | Select | Searchable with Command |
| MultiSelect | Command | With Badge for selections |
| Checkbox | Checkbox | Custom animation |
| Switch | Switch | Smooth transition |
| Slider | Slider | Dual thumb range |
| Modal | Dialog | With motion animation |
| Toast | Sonner | Position: top-right |
| Tooltip | Tooltip | Delay duration 500ms |
| Popover | Popover | With Command for menus |
| DropdownMenu | DropdownMenu | Icon + shortcut keys |
| Tabs | Tabs | Custom underline indicator |
| Breadcrumb | Breadcrumb | Auto-generated from path |
| Pagination | Pagination | With page size selector |
| Card | Card | Custom shadow + hover |
| Avatar | Avatar | With fallback initials |
| Badge | Badge | Color variants |
| Table | Table | Sortable headers |
| Sheet | Sheet | Right/left sides |
| Command | Command | Global search palette |
| Skeleton | Skeleton | Pulse animation |
| Progress | Progress | With percentage label |
| Calendar | Calendar | Locale: zh-CN |

---

## 九、前端开发规范

### 9.1 TailwindCSS 使用规范

```
✅ Do:
  className="flex items-center gap-2 rounded-lg p-4"
  className="text-sm font-medium text-gray-700 dark:text-gray-300"

❌ Don't:
  className="p-[13px] m-[7px]"     // 不使用任意值，用设计系统
  className="text-[#333]"          // 使用语义化颜色变量
```

### 9.2 模块化 CSS 策略

```tsx
// 1. Tailwind 优先 — 95% 样式用 Tailwind 类
// 2. cn() 工具函数合并类名
// 3. 复杂组件用 CSS Module + Tailwind
// 4. 全局样式用 globals.css — 定义 Design Tokens
```

### 9.3 性能规范

```
- 图片: next/image 自动优化
- 字体: next/font 加载 Inter + JetBrains Mono
- 组件: React.lazy + Suspense 代码分割
- 动画: transform + opacity only (GPU加速)
- 列表: useMemo + React.memo 优化渲染
- Infinite scroll: IntersectionObserver
```

---

## 十、WCAG 可访问性规范

| 准则 | 实现 |
|------|------|
| Color contrast | Text: 4.5:1, Large text: 3:1 (AA) |
| Keyboard nav | All interactive elements reachable by Tab |
| Focus visible | Custom focus ring (2px offset) |
| Screen reader | aria-label, aria-description, role attributes |
| Motion reduced | Respect prefers-reduced-motion |
| Semantic HTML | Use proper heading hierarchy (h1->h6) |
| Alt text | All images have meaningful alt text |
| Error messages | Associate errors with inputs via aria-describedby |

---

## 十一、Design System 交付清单

| # | 交付物 | 状态 |
|:-:|--------|:----:|
| 1 | Color System (Light + Dark) | ✅ 已定义 |
| 2 | Typography System | ✅ 已定义 |
| 3 | Spacing System (8pt Grid) | ✅ 已定义 |
| 4 | Border Radius | ✅ 已定义 |
| 5 | Shadow System | ✅ 已定义 |
| 6 | Animation Tokens | ✅ 已定义 |
| 7 | Button Library | ✅ 已定义 |
| 8 | Form Components | ✅ 已定义 |
| 9 | Navigation Components | ✅ 已定义 |
| 10 | Feedback Components | ✅ 已定义 |
| 11 | Data Display Components | ✅ 已定义 |
| 12 | Card Components (8 types) | ✅ 已定义 |
| 13 | Layout System | ✅ 已定义 |
| 14 | Page Designs (7 pages) | ✅ 已定义 |
| 15 | Animation System | ✅ 已定义 |
| 16 | Responsive Strategy | ✅ 已定义 |
| 17 | Component Naming | ✅ 已定义 |
| 18 | shadcn/ui Mapping | ✅ 已定义 |
| 19 | Dev Standards | ✅ 已定义 |
| 20 | WCAG Accessibility | ✅ 已定义 |

---

## 十二、后续步骤

本 UI 设计规范完成后，前端开发可以直接：

1. 按 Design Tokens 配置 `tailwind.config.ts` + `globals.css`
2. 按组件库实现所有基础 UI 组件
3. 按页面设计实现 14 个核心页面
4. 按动画规范添加交互
5. 按响应式方案适配多端

---

## 下一步

[OK] UI 设计规范完成，等待确认后进入 步骤 7：前端开发（Next.js 项目初始化）


