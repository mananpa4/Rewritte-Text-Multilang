const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const TurndownService = require('turndown');
const iconv = require('iconv-lite');

const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced'
});

// Configure Turndown to drop unwanted elements
turndownService.remove(['script', 'style', 'iframe', 'noscript']);

const rootDir = path.join(__dirname, 'docs');
const MAIN_URL = 'https://www.kekenet.com/grammar/left.htm';

// Helper: Delay to prevent rate limiting
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Helper: Sanitize Filenames (Must match scaffold.js logic)
function sanitize(name) {
  return name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '-').replace(/-+/g, '-').toLowerCase();
}

// Helper: Fetch with GBK decoding
async function fetchGbk(url) {
    const res = await fetch(url, {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const buffer = await res.arrayBuffer();
    // Decode GBK to UTF-8
    return iconv.decode(Buffer.from(buffer), 'gbk');
}

// 1. Fetch and Parse Main Page to Build URL Map
async function buildUrlMap() {
    console.log(`Fetching navigation from ${MAIN_URL}...`);
    try {
        const html = await fetchGbk(MAIN_URL);
        const dom = new JSDOM(html);
        const doc = dom.window.document;

        const urlMap = new Map();
        
        const links = doc.querySelectorAll('a');
        links.forEach(a => {
            let text = a.textContent.trim();
            // Remove common whitespace/newline issues in old HTML
            text = text.replace(/[\n\r\t]/g, '').trim();
            
            const href = a.href;
            
            // Filter out anchors and javascript links
            if (text && href && !href.startsWith('javascript') && !href.startsWith('#')) {
                // Determine absolute URL
                // If href is relative (e.g. "0101.htm"), resolve against MAIN_URL base (grammar/)
                // Since MAIN_URL is .../grammar/left.htm, resolving "0101.htm" against it might be tricky if not careful
                // We want https://www.kekenet.com/grammar/0101.htm
                
                // Construct base URL: https://www.kekenet.com/grammar/
                const baseUrl = 'https://www.kekenet.com/grammar/';
                const fullUrl = new URL(href, baseUrl).toString();
                
                urlMap.set(text, fullUrl);
            }
        });

        console.log(`Found ${urlMap.size} links in navigation.`);
        return urlMap;

    } catch (error) {
        console.error('Error fetching navigation:', error);
        return new Map();
    }
}

// 2. Fetch Article Content
async function fetchArticleContent(url) {
    try {
        console.log(`Fetching: ${url}`);
        const html = await fetchGbk(url);
        
        const dom = new JSDOM(html);
        const doc = dom.window.document;

        // Kekenet Article Content Selector
        // Based on analysis of legacy pages: td[width="520"] inside a table
        let contentEl = doc.querySelector('td[width="520"][valign="top"]') || 
                        doc.querySelector('td[width="520"]') ||
                        // Fallback: try to find the main content cell by class p2 if specific width fails
                        Array.from(doc.querySelectorAll('td.p2')).find(el => el.textContent.length > 50 && !el.querySelector('a[href^="#"]'));

        if (!contentEl) {
            console.warn(`  Warning: No content found for ${url}`);
            return null;
        }

        // Cleanup Content
        // Remove ads, google scripts, comments
        const unwanted = contentEl.querySelectorAll('script, style, iframe, font[color="#FF0000"]');
        unwanted.forEach(el => el.remove());

        // Convert to Markdown
        let markdown = turndownService.turndown(contentEl.innerHTML);
        
        return markdown;

    } catch (error) {
        console.error(`  Error fetching ${url}:`, error.message);
        return null;
    }
}

// 3. Main Hydration Logic
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
      "many, much", "few,little,a few,ները"
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

async function main() {
    const urlMap = await buildUrlMap();
    
    // Iterate through all sections and items
    for (const section of navigationData) {
        console.log(`Processing Section: ${section.category}`);
        const sectionPath = path.join(rootDir, section.slug);

        for (const item of section.items) {
            const filename = sanitize(item) + '.md';
            const filePath = path.join(sectionPath, filename);
            
            // Look up URL
            const itemUrl = urlMap.get(item);
            
            if (!itemUrl) {
                console.warn(`  [SKIP] URL not found for item: ${item}`);
                continue;
            }

            // Fetch Content
            const markdownContent = await fetchArticleContent(itemUrl);
            
            if (markdownContent) {
                // Add Frontmatter and Title
                const fileContent = `# ${item}\n\nSources: [Original Article](${itemUrl})\n\n${markdownContent}`;
                fs.writeFileSync(filePath, fileContent);
                console.log(`  [OK] Updated ${filename}`);
            }
            
            // Respectful crawling delay
            await delay(1000); 
        }
    }
    console.log("Hydration Complete!");
}

main();
