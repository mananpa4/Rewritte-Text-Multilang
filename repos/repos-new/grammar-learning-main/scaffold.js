const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, 'docs');

// 1. The Data Source
const navigationData = [
  {
    "category": "名词",
    "slug": "nouns",
    "items": [
      "名词复数的规则变化", "其它名词复数的规则变化", "名词复数的不规则变化",
      "不可数名词量的表示", "定语名词的复数", "不同国家的人的单复数", "名词的格"
    ]
  },
  {
    "category": "冠词和数词",
    "slug": "articles-numerals",
    "items": [
      "不定冠词的用法", "定冠词的用法", "零冠词的用法",
      "冠词与形容词+名词结构", "冠词位置", "数词"
    ]
  },
  {
    "category": "代词",
    "slug": "pronouns",
    "items": [
      "人称代词的用法", "人称代词之主、宾格的替换", "代词的指代问题",
      "并列人称代词的排列顺序", "物主代词", "双重所有格", "反身代词", "相互代词",
      "指示代词", "疑问代词", "关系代词", "every,no,all,both,...",
      "none,few,some,any,...", "代词比较辩异one,that和it", "one/another/the other",
      "\"the\"的妙用", "anyone/any one;...", "both,either,neither,...",
      "many, much", "few,little,a few,..."
    ]
  },
  {
    "category": "形容词和副词",
    "slug": "adjectives-adverbs",
    "items": [
      "形容词及其用法", "以-ly结尾的形容词", "用形容词表示类别和整体",
      "多个形容词修饰名词的顺序", "副词及其基本用法", "兼有两种形式的副词",
      "形容词与副词的比较级", "as+形容词或副词原级+as", "比较级形容词或副词+than",
      "可修饰比较级的词", "many,old和far", "the+最高级+比较范围", "和more有关的词组"
    ]
  },
  {
    "category": "动词",
    "slug": "verbs",
    "items": [
      "系动词", "什么是助动词", "助动词be的用法", "助动词have的用法",
      "助动词do 的用法", "助动词shall和will的用法", "助动词should,would的用法",
      "短语动词", "非谓语动词"
    ]
  },
  {
    "category": "动名词",
    "slug": "gerunds",
    "items": [
      "动名词作主语、宾语和表语", "worth 的用法"
    ]
  },
  {
    "category": "动词不定式",
    "slug": "infinitives",
    "items": [
      "不定式作宾语", "不定式作补语", "不定式主语", "It's for sb/It's of sb",
      "不定式作表语", "不定式作定语", "不定式作状语", "用作介词的to",
      "省to 的动词不定式", "动词不定式的否定式", "不定式特殊句型too…to…",
      "不定式特殊句型so as to", "不定式特殊句型Why not", "不定式的时态和语态",
      "动名词与不定式"
    ]
  },
  {
    "category": "特殊词精讲",
    "slug": "special-words",
    "items": [
      "stop doing/to do", "forget doing/to do", "remember doing/to do",
      "regret doing/to do", "cease doing/to do", "try doing/to do",
      "go on doing/to do", "be afraid doing/to do", "be interested doing/...",
      "mean doing/to do", "begin(start) doing/to do", "感官动词+ doing/to do"
    ]
  },
  {
    "category": "分词",
    "slug": "participles",
    "items": [
      "分词作定语", "分词作状语", "连词+分词(短语)", "分词作补语",
      "分词作表语", "分词作插入语", "分词的时态", "分词的语态"
    ]
  },
  {
    "category": "独立主格",
    "slug": "absolute-construction",
    "items": [
      "独立主格", "With的复合结构"
    ]
  },
  {
    "category": "动词的时态",
    "slug": "verb-tenses",
    "items": [
      "一般现在时的用法", "一般过去时的用法", "used to/be used to",
      "一般将来时", "be going to/will", "be to和be going to",
      "一般现在时表将来", "用现在进行时表示将来", "现在完成时",
      "比较过去时与现在完成时", "用于现在完成时的句型", "比较since和for",
      "since的四种用法", "延续动词与瞬间动词", "过去完成时",
      "用一般过去时代替完成时", "将来完成时", "现在进行时",
      "不用进行时的动词", "过去进行时", "将来进行时",
      "一般现在时代替将来时", "一般现在时代替过去时", "一般现在时代替完成时",
      "一般现在时代替进行时", "现在进行时代替将来时", "时态一致", "时态与时间状语"
    ]
  },
  {
    "category": "动词的语态",
    "slug": "verb-voices",
    "items": [
      "let 的用法", "短语动词的被动语态", "表示\"据说\"或\"相信\"的词组",
      "不用被动语态的情况", "主动形式表示被动意义", "被动形式表示主动意义",
      "need/want/require/worth"
    ]
  },
  {
    "category": "句子的种类",
    "slug": "sentence-types",
    "items": [
      "句子的种类", "感叹句结构", "强调句结构", "用助动词进行强调", "反意疑问句"
    ]
  },
  {
    "category": "倒装",
    "slug": "inversion",
    "items": [
      "倒装句之全部倒装", "倒装句之部分倒装", "以否定词开头作部分倒装",
      "so,either,nor作部分倒装", "only在句首要倒装的情况", "as,though引导的倒装句",
      "其他部分倒装"
    ]
  },
  {
    "category": "主谓一致",
    "slug": "subject-verb-agreement",
    "items": [
      "并列结构作主语谓语用复数", "主谓一致中的靠近原则", "谓语动词与前面的主语一致",
      "谓语需用单数", "指代意义决定谓语的单复数", "与后接名词或代词保持一致"
    ]
  },
  {
    "category": "虚拟语气",
    "slug": "subjunctive-mood",
    "items": [
      "真实条件句", "非真实条件句", "混合条件句", "虚拟条件句的倒装",
      "特殊的虚拟语气词：should", "wish的用法", "比较if only与only if",
      "It is (high) time that", "need\"不必做\"和\"本不该做\""
    ]
  },
  {
    "category": "名词性从句",
    "slug": "noun-clauses",
    "items": [
      "引导名词性从句的连接词", "名词性that-从句", "名词性wh-从句",
      "if,whether引导的名词从句", "否定转移"
    ]
  },
  {
    "category": "定语从句",
    "slug": "attributive-clauses",
    "items": [
      "关系代词引导的定语从句", "关系副词引导的定语从句", "判断关系代词与关系副词",
      "限制性和非限制性定语从句", "介词+关系词", "as,which非限定性定语从句",
      "先行词和关系词二合一", "what/whatever/that...", "关系代词that的用法"
    ]
  },
  {
    "category": "状语从句",
    "slug": "adverbial-clauses",
    "items": [
      "地点状语从句", "方式状语从句", "原因状语从句", "目的状语从句",
      "结果状语从句", "条件状语从句", "让步状语从句", "比较while, when, as",
      "比较until和till", "表示\"一…就…\"的结构"
    ]
  },
  {
    "category": "连词",
    "slug": "conjunctions",
    "items": [
      "并列连词与并列结构", "比较and和or", "表示选择的并列结构",
      "表示转折或对比", "表原因关系", "比较so和such"
    ]
  },
  {
    "category": "情态动词",
    "slug": "modal-verbs",
    "items": [
      "情态动词的语法特征", "比较can 和be able to", "比较may和might",
      "比较have to和must", "must表示推测", "表示推测的用法",
      "情态动词+have+过去分词", "should和ought to", "had better表示最好",
      "would rather表示\"宁愿\"", "will和would", "情态动词的回答方式",
      "带to的情态动词", "比较need和dare"
    ]
  }
];

// 2. Helper to sanitize filenames
function sanitize(name) {
  // Replace characters that are unsafe for filenames or URLs with dashes
  // Keep Chinese characters, letters, and numbers
  // This version is simpler and less prone to syntax errors in tooling
  return name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '-').replace(/-+/g, '-').toLowerCase();
}

// 3. Main Generation Logic
if (!fs.existsSync(rootDir)) {
  fs.mkdirSync(rootDir);
}

const sidebarConfig = [];

navigationData.forEach(section => {
  const sectionPath = path.join(rootDir, section.slug);
  if (!fs.existsSync(sectionPath)) {
    fs.mkdirSync(sectionPath);
  }

  const sidebarGroup = {
    text: section.category,
    collapsed: true, // Default to collapsed to save space
    items: []
  };

  section.items.forEach(item => {
    const filename = sanitize(item) + '.md';
    const filePath = path.join(sectionPath, filename);
    // Construct link relative to .vitepress/config.mjs which is handled by VitePress router
    const link = `/${section.slug}/${sanitize(item)}`;

    // Create Markdown Content
    const content = `# ${item}\n\n此处是关于 **${item}** 的详细语法讲解。\n\n> 内容整理中...\n\n## 核心要点\n\n- [ ] 待补充规则定义\n- [ ] 待补充例句\n`;
    
    fs.writeFileSync(filePath, content);

    // Add to sidebar
    sidebarGroup.items.push({
      text: item,
      link: link
    });
  });

  sidebarConfig.push(sidebarGroup);
});

// 4. Create Landing Page
const indexContent = `---\nlayout: home\n
hero:
  name: "英语语法大全"
  text: "结构化英语语法知识库"
  tagline: "基于可可英语语法分类整理"
  actions:
    - theme: brand
      text: 开始学习
      link: /nouns/${sanitize(navigationData[0].items[0])}
    - theme: alt
      text: GitHub
      link: https://github.com/vuejs/vitepress

features:
  - title: 体系完备
    details: 涵盖名词、动词、从句等21个核心语法分类。
  - title: 结构清晰
    details: 依照经典语法教材结构，由浅入深。
  - title: 便捷查阅
    details: 左侧导航栏快速定位，随时查阅具体知识点。
---\n`;

fs.writeFileSync(path.join(rootDir, 'index.md'), indexContent);


// 5. Create Config File
const configPath = path.join(rootDir, '.vitepress');
if (!fs.existsSync(configPath)) {
  fs.mkdirSync(configPath);
}

// Ensure proper indentation for the generated file
const sidebarJson = JSON.stringify(sidebarConfig, null, 2);

const configContent = `import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "英语语法大全",
  description: "English Grammar Encyclopedia",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '名词', link: '/nouns/名词复数的规则变化' },
      { text: '动词', link: '/verbs/系动词' }
    ],

    sidebar: ${sidebarJson},

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ],
    
    search: {
      provider: 'local'
    }
  }
})
`;

fs.writeFileSync(path.join(configPath, 'config.mjs'), configContent);

console.log("Site generation complete!");