import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "英语语法大全",
  description: "English Grammar Encyclopedia",
  base: "/grammar-learning/",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '名词', link: '/nouns/名词复数的规则变化' },
      { text: '动词', link: '/verbs/系动词' }
    ],

    sidebar: [
      {
        "text": "名词",
        "collapsed": true,
        "items": [
          {
            "text": "名词复数的规则变化",
            "link": "/nouns/名词复数的规则变化"
          },
          {
            "text": "其它名词复数的规则变化",
            "link": "/nouns/其它名词复数的规则变化"
          },
          {
            "text": "名词复数的不规则变化",
            "link": "/nouns/名词复数的不规则变化"
          },
          {
            "text": "不可数名词量的表示",
            "link": "/nouns/不可数名词量的表示"
          },
          {
            "text": "定语名词的复数",
            "link": "/nouns/定语名词的复数"
          },
          {
            "text": "不同国家的人的单复数",
            "link": "/nouns/不同国家的人的单复数"
          },
          {
            "text": "名词的格",
            "link": "/nouns/名词的格"
          }
        ]
      },
      {
        "text": "冠词和数词",
        "collapsed": true,
        "items": [
          {
            "text": "不定冠词的用法",
            "link": "/articles-numerals/不定冠词的用法"
          },
          {
            "text": "定冠词的用法",
            "link": "/articles-numerals/定冠词的用法"
          },
          {
            "text": "零冠词的用法",
            "link": "/articles-numerals/零冠词的用法"
          },
          {
            "text": "冠词与形容词+名词结构",
            "link": "/articles-numerals/冠词与形容词-名词结构"
          },
          {
            "text": "冠词位置",
            "link": "/articles-numerals/冠词位置"
          },
          {
            "text": "数词",
            "link": "/articles-numerals/数词"
          }
        ]
      },
      {
        "text": "代词",
        "collapsed": true,
        "items": [
          {
            "text": "人称代词的用法",
            "link": "/pronouns/人称代词的用法"
          },
          {
            "text": "人称代词之主、宾格的替换",
            "link": "/pronouns/人称代词之主-宾格的替换"
          },
          {
            "text": "代词的指代问题",
            "link": "/pronouns/代词的指代问题"
          },
          {
            "text": "并列人称代词的排列顺序",
            "link": "/pronouns/并列人称代词的排列顺序"
          },
          {
            "text": "物主代词",
            "link": "/pronouns/物主代词"
          },
          {
            "text": "双重所有格",
            "link": "/pronouns/双重所有格"
          },
          {
            "text": "反身代词",
            "link": "/pronouns/反身代词"
          },
          {
            "text": "相互代词",
            "link": "/pronouns/相互代词"
          },
          {
            "text": "指示代词",
            "link": "/pronouns/指示代词"
          },
          {
            "text": "疑问代词",
            "link": "/pronouns/疑问代词"
          },
          {
            "text": "关系代词",
            "link": "/pronouns/关系代词"
          },
          {
            "text": "every,no,all,both,...",
            "link": "/pronouns/every-no-all-both-"
          },
          {
            "text": "none,few,some,any,...",
            "link": "/pronouns/none-few-some-any-"
          },
          {
            "text": "代词比较辩异one,that和it",
            "link": "/pronouns/代词比较辩异one-that和it"
          },
          {
            "text": "one/another/the other",
            "link": "/pronouns/one-another-the-other"
          },
          {
            "text": "\"the\"的妙用",
            "link": "/pronouns/-the-的妙用"
          },
          {
            "text": "anyone/any one;...",
            "link": "/pronouns/anyone-any-one-"
          },
          {
            "text": "both,either,neither,...",
            "link": "/pronouns/both-either-neither-"
          },
          {
            "text": "many, much",
            "link": "/pronouns/many-much"
          },
          {
            "text": "few,little,a few,...",
            "link": "/pronouns/few-little-a-few-"
          }
        ]
      },
      {
        "text": "形容词和副词",
        "collapsed": true,
        "items": [
          {
            "text": "形容词及其用法",
            "link": "/adjectives-adverbs/形容词及其用法"
          },
          {
            "text": "以-ly结尾的形容词",
            "link": "/adjectives-adverbs/以-ly结尾的形容词"
          },
          {
            "text": "用形容词表示类别和整体",
            "link": "/adjectives-adverbs/用形容词表示类别和整体"
          },
          {
            "text": "多个形容词修饰名词的顺序",
            "link": "/adjectives-adverbs/多个形容词修饰名词的顺序"
          },
          {
            "text": "副词及其基本用法",
            "link": "/adjectives-adverbs/副词及其基本用法"
          },
          {
            "text": "兼有两种形式的副词",
            "link": "/adjectives-adverbs/兼有两种形式的副词"
          },
          {
            "text": "形容词与副词的比较级",
            "link": "/adjectives-adverbs/形容词与副词的比较级"
          },
          {
            "text": "as+形容词或副词原级+as",
            "link": "/adjectives-adverbs/as-形容词或副词原级-as"
          },
          {
            "text": "比较级形容词或副词+than",
            "link": "/adjectives-adverbs/比较级形容词或副词-than"
          },
          {
            "text": "可修饰比较级的词",
            "link": "/adjectives-adverbs/可修饰比较级的词"
          },
          {
            "text": "many,old和far",
            "link": "/adjectives-adverbs/many-old和far"
          },
          {
            "text": "the+最高级+比较范围",
            "link": "/adjectives-adverbs/the-最高级-比较范围"
          },
          {
            "text": "和more有关的词组",
            "link": "/adjectives-adverbs/和more有关的词组"
          }
        ]
      },
      {
        "text": "动词",
        "collapsed": true,
        "items": [
          {
            "text": "系动词",
            "link": "/verbs/系动词"
          },
          {
            "text": "什么是助动词",
            "link": "/verbs/什么是助动词"
          },
          {
            "text": "助动词be的用法",
            "link": "/verbs/助动词be的用法"
          },
          {
            "text": "助动词have的用法",
            "link": "/verbs/助动词have的用法"
          },
          {
            "text": "助动词do 的用法",
            "link": "/verbs/助动词do-的用法"
          },
          {
            "text": "助动词shall和will的用法",
            "link": "/verbs/助动词shall和will的用法"
          },
          {
            "text": "助动词should,would的用法",
            "link": "/verbs/助动词should-would的用法"
          },
          {
            "text": "短语动词",
            "link": "/verbs/短语动词"
          },
          {
            "text": "非谓语动词",
            "link": "/verbs/非谓语动词"
          }
        ]
      },
      {
        "text": "动名词",
        "collapsed": true,
        "items": [
          {
            "text": "动名词作主语、宾语和表语",
            "link": "/gerunds/动名词作主语-宾语和表语"
          },
          {
            "text": "worth 的用法",
            "link": "/gerunds/worth-的用法"
          }
        ]
      },
      {
        "text": "动词不定式",
        "collapsed": true,
        "items": [
          {
            "text": "不定式作宾语",
            "link": "/infinitives/不定式作宾语"
          },
          {
            "text": "不定式作补语",
            "link": "/infinitives/不定式作补语"
          },
          {
            "text": "不定式主语",
            "link": "/infinitives/不定式主语"
          },
          {
            "text": "It's for sb/It's of sb",
            "link": "/infinitives/it-s-for-sb-it-s-of-sb"
          },
          {
            "text": "不定式作表语",
            "link": "/infinitives/不定式作表语"
          },
          {
            "text": "不定式作定语",
            "link": "/infinitives/不定式作定语"
          },
          {
            "text": "不定式作状语",
            "link": "/infinitives/不定式作状语"
          },
          {
            "text": "用作介词的to",
            "link": "/infinitives/用作介词的to"
          },
          {
            "text": "省to 的动词不定式",
            "link": "/infinitives/省to-的动词不定式"
          },
          {
            "text": "动词不定式的否定式",
            "link": "/infinitives/动词不定式的否定式"
          },
          {
            "text": "不定式特殊句型too…to…",
            "link": "/infinitives/不定式特殊句型too-to-"
          },
          {
            "text": "不定式特殊句型so as to",
            "link": "/infinitives/不定式特殊句型so-as-to"
          },
          {
            "text": "不定式特殊句型Why not",
            "link": "/infinitives/不定式特殊句型why-not"
          },
          {
            "text": "不定式的时态和语态",
            "link": "/infinitives/不定式的时态和语态"
          },
          {
            "text": "动名词与不定式",
            "link": "/infinitives/动名词与不定式"
          }
        ]
      },
      {
        "text": "特殊词精讲",
        "collapsed": true,
        "items": [
          {
            "text": "stop doing/to do",
            "link": "/special-words/stop-doing-to-do"
          },
          {
            "text": "forget doing/to do",
            "link": "/special-words/forget-doing-to-do"
          },
          {
            "text": "remember doing/to do",
            "link": "/special-words/remember-doing-to-do"
          },
          {
            "text": "regret doing/to do",
            "link": "/special-words/regret-doing-to-do"
          },
          {
            "text": "cease doing/to do",
            "link": "/special-words/cease-doing-to-do"
          },
          {
            "text": "try doing/to do",
            "link": "/special-words/try-doing-to-do"
          },
          {
            "text": "go on doing/to do",
            "link": "/special-words/go-on-doing-to-do"
          },
          {
            "text": "be afraid doing/to do",
            "link": "/special-words/be-afraid-doing-to-do"
          },
          {
            "text": "be interested doing/...",
            "link": "/special-words/be-interested-doing-"
          },
          {
            "text": "mean doing/to do",
            "link": "/special-words/mean-doing-to-do"
          },
          {
            "text": "begin(start) doing/to do",
            "link": "/special-words/begin-start-doing-to-do"
          },
          {
            "text": "感官动词+ doing/to do",
            "link": "/special-words/感官动词-doing-to-do"
          }
        ]
      },
      {
        "text": "分词",
        "collapsed": true,
        "items": [
          {
            "text": "分词作定语",
            "link": "/participles/分词作定语"
          },
          {
            "text": "分词作状语",
            "link": "/participles/分词作状语"
          },
          {
            "text": "连词+分词(短语)",
            "link": "/participles/连词-分词-短语-"
          },
          {
            "text": "分词作补语",
            "link": "/participles/分词作补语"
          },
          {
            "text": "分词作表语",
            "link": "/participles/分词作表语"
          },
          {
            "text": "分词作插入语",
            "link": "/participles/分词作插入语"
          },
          {
            "text": "分词的时态",
            "link": "/participles/分词的时态"
          },
          {
            "text": "分词的语态",
            "link": "/participles/分词的语态"
          }
        ]
      },
      {
        "text": "独立主格",
        "collapsed": true,
        "items": [
          {
            "text": "独立主格",
            "link": "/absolute-construction/独立主格"
          },
          {
            "text": "With的复合结构",
            "link": "/absolute-construction/with的复合结构"
          }
        ]
      },
      {
        "text": "动词的时态",
        "collapsed": true,
        "items": [
          {
            "text": "一般现在时的用法",
            "link": "/verb-tenses/一般现在时的用法"
          },
          {
            "text": "一般过去时的用法",
            "link": "/verb-tenses/一般过去时的用法"
          },
          {
            "text": "used to/be used to",
            "link": "/verb-tenses/used-to-be-used-to"
          },
          {
            "text": "一般将来时",
            "link": "/verb-tenses/一般将来时"
          },
          {
            "text": "be going to/will",
            "link": "/verb-tenses/be-going-to-will"
          },
          {
            "text": "be to和be going to",
            "link": "/verb-tenses/be-to和be-going-to"
          },
          {
            "text": "一般现在时表将来",
            "link": "/verb-tenses/一般现在时表将来"
          },
          {
            "text": "用现在进行时表示将来",
            "link": "/verb-tenses/用现在进行时表示将来"
          },
          {
            "text": "现在完成时",
            "link": "/verb-tenses/现在完成时"
          },
          {
            "text": "比较过去时与现在完成时",
            "link": "/verb-tenses/比较过去时与现在完成时"
          },
          {
            "text": "用于现在完成时的句型",
            "link": "/verb-tenses/用于现在完成时的句型"
          },
          {
            "text": "比较since和for",
            "link": "/verb-tenses/比较since和for"
          },
          {
            "text": "since的四种用法",
            "link": "/verb-tenses/since的四种用法"
          },
          {
            "text": "延续动词与瞬间动词",
            "link": "/verb-tenses/延续动词与瞬间动词"
          },
          {
            "text": "过去完成时",
            "link": "/verb-tenses/过去完成时"
          },
          {
            "text": "用一般过去时代替完成时",
            "link": "/verb-tenses/用一般过去时代替完成时"
          },
          {
            "text": "将来完成时",
            "link": "/verb-tenses/将来完成时"
          },
          {
            "text": "现在进行时",
            "link": "/verb-tenses/现在进行时"
          },
          {
            "text": "不用进行时的动词",
            "link": "/verb-tenses/不用进行时的动词"
          },
          {
            "text": "过去进行时",
            "link": "/verb-tenses/过去进行时"
          },
          {
            "text": "将来进行时",
            "link": "/verb-tenses/将来进行时"
          },
          {
            "text": "一般现在时代替将来时",
            "link": "/verb-tenses/一般现在时代替将来时"
          },
          {
            "text": "一般现在时代替过去时",
            "link": "/verb-tenses/一般现在时代替过去时"
          },
          {
            "text": "一般现在时代替完成时",
            "link": "/verb-tenses/一般现在时代替完成时"
          },
          {
            "text": "一般现在时代替进行时",
            "link": "/verb-tenses/一般现在时代替进行时"
          },
          {
            "text": "现在进行时代替将来时",
            "link": "/verb-tenses/现在进行时代替将来时"
          },
          {
            "text": "时态一致",
            "link": "/verb-tenses/时态一致"
          },
          {
            "text": "时态与时间状语",
            "link": "/verb-tenses/时态与时间状语"
          }
        ]
      },
      {
        "text": "动词的语态",
        "collapsed": true,
        "items": [
          {
            "text": "let 的用法",
            "link": "/verb-voices/let-的用法"
          },
          {
            "text": "短语动词的被动语态",
            "link": "/verb-voices/短语动词的被动语态"
          },
          {
            "text": "表示\"据说\"或\"相信\"的词组",
            "link": "/verb-voices/表示-据说-或-相信-的词组"
          },
          {
            "text": "不用被动语态的情况",
            "link": "/verb-voices/不用被动语态的情况"
          },
          {
            "text": "主动形式表示被动意义",
            "link": "/verb-voices/主动形式表示被动意义"
          },
          {
            "text": "被动形式表示主动意义",
            "link": "/verb-voices/被动形式表示主动意义"
          },
          {
            "text": "need/want/require/worth",
            "link": "/verb-voices/need-want-require-worth"
          }
        ]
      },
      {
        "text": "句子的种类",
        "collapsed": true,
        "items": [
          {
            "text": "句子的种类",
            "link": "/sentence-types/句子的种类"
          },
          {
            "text": "感叹句结构",
            "link": "/sentence-types/感叹句结构"
          },
          {
            "text": "强调句结构",
            "link": "/sentence-types/强调句结构"
          },
          {
            "text": "用助动词进行强调",
            "link": "/sentence-types/用助动词进行强调"
          },
          {
            "text": "反意疑问句",
            "link": "/sentence-types/反意疑问句"
          }
        ]
      },
      {
        "text": "倒装",
        "collapsed": true,
        "items": [
          {
            "text": "倒装句之全部倒装",
            "link": "/inversion/倒装句之全部倒装"
          },
          {
            "text": "倒装句之部分倒装",
            "link": "/inversion/倒装句之部分倒装"
          },
          {
            "text": "以否定词开头作部分倒装",
            "link": "/inversion/以否定词开头作部分倒装"
          },
          {
            "text": "so,either,nor作部分倒装",
            "link": "/inversion/so-either-nor作部分倒装"
          },
          {
            "text": "only在句首要倒装的情况",
            "link": "/inversion/only在句首要倒装的情况"
          },
          {
            "text": "as,though引导的倒装句",
            "link": "/inversion/as-though引导的倒装句"
          },
          {
            "text": "其他部分倒装",
            "link": "/inversion/其他部分倒装"
          }
        ]
      },
      {
        "text": "主谓一致",
        "collapsed": true,
        "items": [
          {
            "text": "并列结构作主语谓语用复数",
            "link": "/subject-verb-agreement/并列结构作主语谓语用复数"
          },
          {
            "text": "主谓一致中的靠近原则",
            "link": "/subject-verb-agreement/主谓一致中的靠近原则"
          },
          {
            "text": "谓语动词与前面的主语一致",
            "link": "/subject-verb-agreement/谓语动词与前面的主语一致"
          },
          {
            "text": "谓语需用单数",
            "link": "/subject-verb-agreement/谓语需用单数"
          },
          {
            "text": "指代意义决定谓语的单复数",
            "link": "/subject-verb-agreement/指代意义决定谓语的单复数"
          },
          {
            "text": "与后接名词或代词保持一致",
            "link": "/subject-verb-agreement/与后接名词或代词保持一致"
          }
        ]
      },
      {
        "text": "虚拟语气",
        "collapsed": true,
        "items": [
          {
            "text": "真实条件句",
            "link": "/subjunctive-mood/真实条件句"
          },
          {
            "text": "非真实条件句",
            "link": "/subjunctive-mood/非真实条件句"
          },
          {
            "text": "混合条件句",
            "link": "/subjunctive-mood/混合条件句"
          },
          {
            "text": "虚拟条件句的倒装",
            "link": "/subjunctive-mood/虚拟条件句的倒装"
          },
          {
            "text": "特殊的虚拟语气词：should",
            "link": "/subjunctive-mood/特殊的虚拟语气词-should"
          },
          {
            "text": "wish的用法",
            "link": "/subjunctive-mood/wish的用法"
          },
          {
            "text": "比较if only与only if",
            "link": "/subjunctive-mood/比较if-only与only-if"
          },
          {
            "text": "It is (high) time that",
            "link": "/subjunctive-mood/it-is-high-time-that"
          },
          {
            "text": "need\"不必做\"和\"本不该做\"",
            "link": "/subjunctive-mood/need-不必做-和-本不该做-"
          }
        ]
      },
      {
        "text": "名词性从句",
        "collapsed": true,
        "items": [
          {
            "text": "引导名词性从句的连接词",
            "link": "/noun-clauses/引导名词性从句的连接词"
          },
          {
            "text": "名词性that-从句",
            "link": "/noun-clauses/名词性that-从句"
          },
          {
            "text": "名词性wh-从句",
            "link": "/noun-clauses/名词性wh-从句"
          },
          {
            "text": "if,whether引导的名词从句",
            "link": "/noun-clauses/if-whether引导的名词从句"
          },
          {
            "text": "否定转移",
            "link": "/noun-clauses/否定转移"
          }
        ]
      },
      {
        "text": "定语从句",
        "collapsed": true,
        "items": [
          {
            "text": "关系代词引导的定语从句",
            "link": "/attributive-clauses/关系代词引导的定语从句"
          },
          {
            "text": "关系副词引导的定语从句",
            "link": "/attributive-clauses/关系副词引导的定语从句"
          },
          {
            "text": "判断关系代词与关系副词",
            "link": "/attributive-clauses/判断关系代词与关系副词"
          },
          {
            "text": "限制性和非限制性定语从句",
            "link": "/attributive-clauses/限制性和非限制性定语从句"
          },
          {
            "text": "介词+关系词",
            "link": "/attributive-clauses/介词-关系词"
          },
          {
            "text": "as,which非限定性定语从句",
            "link": "/attributive-clauses/as-which非限定性定语从句"
          },
          {
            "text": "先行词和关系词二合一",
            "link": "/attributive-clauses/先行词和关系词二合一"
          },
          {
            "text": "what/whatever/that...",
            "link": "/attributive-clauses/what-whatever-that-"
          },
          {
            "text": "关系代词that的用法",
            "link": "/attributive-clauses/关系代词that的用法"
          }
        ]
      },
      {
        "text": "状语从句",
        "collapsed": true,
        "items": [
          {
            "text": "地点状语从句",
            "link": "/adverbial-clauses/地点状语从句"
          },
          {
            "text": "方式状语从句",
            "link": "/adverbial-clauses/方式状语从句"
          },
          {
            "text": "原因状语从句",
            "link": "/adverbial-clauses/原因状语从句"
          },
          {
            "text": "目的状语从句",
            "link": "/adverbial-clauses/目的状语从句"
          },
          {
            "text": "结果状语从句",
            "link": "/adverbial-clauses/结果状语从句"
          },
          {
            "text": "条件状语从句",
            "link": "/adverbial-clauses/条件状语从句"
          },
          {
            "text": "让步状语从句",
            "link": "/adverbial-clauses/让步状语从句"
          },
          {
            "text": "比较while, when, as",
            "link": "/adverbial-clauses/比较while-when-as"
          },
          {
            "text": "比较until和till",
            "link": "/adverbial-clauses/比较until和till"
          },
          {
            "text": "表示\"一…就…\"的结构",
            "link": "/adverbial-clauses/表示-一-就-的结构"
          }
        ]
      },
      {
        "text": "连词",
        "collapsed": true,
        "items": [
          {
            "text": "并列连词与并列结构",
            "link": "/conjunctions/并列连词与并列结构"
          },
          {
            "text": "比较and和or",
            "link": "/conjunctions/比较and和or"
          },
          {
            "text": "表示选择的并列结构",
            "link": "/conjunctions/表示选择的并列结构"
          },
          {
            "text": "表示转折或对比",
            "link": "/conjunctions/表示转折或对比"
          },
          {
            "text": "表原因关系",
            "link": "/conjunctions/表原因关系"
          },
          {
            "text": "比较so和such",
            "link": "/conjunctions/比较so和such"
          }
        ]
      },
      {
        "text": "情态动词",
        "collapsed": true,
        "items": [
          {
            "text": "情态动词的语法特征",
            "link": "/modal-verbs/情态动词的语法特征"
          },
          {
            "text": "比较can 和be able to",
            "link": "/modal-verbs/比较can-和be-able-to"
          },
          {
            "text": "比较may和might",
            "link": "/modal-verbs/比较may和might"
          },
          {
            "text": "比较have to和must",
            "link": "/modal-verbs/比较have-to和must"
          },
          {
            "text": "must表示推测",
            "link": "/modal-verbs/must表示推测"
          },
          {
            "text": "表示推测的用法",
            "link": "/modal-verbs/表示推测的用法"
          },
          {
            "text": "情态动词+have+过去分词",
            "link": "/modal-verbs/情态动词-have-过去分词"
          },
          {
            "text": "should和ought to",
            "link": "/modal-verbs/should和ought-to"
          },
          {
            "text": "had better表示最好",
            "link": "/modal-verbs/had-better表示最好"
          },
          {
            "text": "would rather表示\"宁愿\"",
            "link": "/modal-verbs/would-rather表示-宁愿-"
          },
          {
            "text": "will和would",
            "link": "/modal-verbs/will和would"
          },
          {
            "text": "情态动词的回答方式",
            "link": "/modal-verbs/情态动词的回答方式"
          },
          {
            "text": "带to的情态动词",
            "link": "/modal-verbs/带to的情态动词"
          },
          {
            "text": "比较need和dare",
            "link": "/modal-verbs/比较need和dare"
          }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ],

    search: {
      provider: 'local'
    }
  }
})
