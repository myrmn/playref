import { LanguageCode } from "./types";

export interface TranslationDictionary {
  appName: string;
  tagline: string;
  homeHeadline: string;
  homeSubline: string;
  inputPlaceholder: string;
  send: string;
  stop: string;
  about: string;
  aboutView: {
    badge: string;
    title: string;
    subtitle: string;
    whatIsPlayRef: string;
    whatIsPlayRefDesc: string;
    featuresTitle: string;
    feature1Title: string;
    feature1Desc: string;
    feature2Title: string;
    feature2Desc: string;
    feature3Title: string;
    feature3Desc: string;
    feature4Title: string;
    feature4Desc: string;
    howItWorksTitle: string;
    step1Title: string;
    step1Desc: string;
    step2Title: string;
    step2Desc: string;
    step3Title: string;
    step3Desc: string;
    refereeNoticeTitle: string;
    refereeNoticeDesc: string;
    ctaButton: string;
    browseLawsBtn: string;
  };
  lawBrowser: string;
  newChat: string;
  recentChats: string;
  noRecentChats: string;
  suggestedPrompts: {
    title: string;
    description: string;
    prompt: string;
  }[];
  stages: {
    routing: string;
    searching: string;
    checking: string;
    writing: string;
  };
  answerCard: {
    shortAnswer: string;
    applicableLaws: string;
    possibleInterpretations: string;
    whatWouldChange: string;
    assumptions: string;
    clarifyingDetail: string;
    submitClarification: string;
    orCustomAnswer: string;
    feedbackHelpful: string;
    feedbackNotHelpful: string;
    wrongLawCited: string;
    feedbackThanks: string;
  };
  citationDrawer: {
    title: string;
    officialText: string;
    law: string;
    page: string;
    edition: string;
    source: string;
    copyCitation: string;
    citationCopied: string;
    openInLawBrowser: string;
    close: string;
  };
  lawBrowserView: {
    title: string;
    searchPlaceholder: string;
    allLaws: string;
    chunksCount: string;
    askAboutSection: string;
    selectLawPrompt: string;
    loadingLaw: string;
    emptySearchResults: string;
  };
  feedbackModal: {
    title: string;
    subtitle: string;
    optionWrongLaw: string;
    optionMissingLaw: string;
    optionUnclear: string;
    optionOther: string;
    commentPlaceholder: string;
    submit: string;
    cancel: string;
  };
  disclaimer: string;
  status: {
    connected: string;
    connecting: string;
    error: string;
    rateLimited: string;
  };
}

export const translations: Record<LanguageCode, TranslationDictionary> = {
  en: {
    appName: "PlayRef",
    tagline: "Football Laws of the Game Assistant",
    homeHeadline: "Ask anything about the Laws of the Game",
    homeSubline: "Answers grounded in the official IFAB Laws of the Game, with verifiable citations.",
    inputPlaceholder: "Describe a situation or ask about a Law (e.g. 'Can a player score from a goal kick?')...",
    send: "Send",
    stop: "Stop",
    about: "About",
    aboutView: {
      badge: "Rules Made Simple",
      title: "What is PlayRef?",
      subtitle: "Your friendly guide to football's official rules. No confusing jargon, no guessing—just clear answers directly from the official IFAB rulebook.",
      whatIsPlayRef: "Why does PlayRef exist?",
      whatIsPlayRefDesc: "Have you ever argued with friends about a referee's controversial call? Wondered why a goal was disallowed after an accidental handball? Or wanted to know if a player can score directly from a throw-in? Football rules can sometimes feel complicated. PlayRef exists to help fans, players, and coaches understand what the rules actually say in plain everyday language.",
      featuresTitle: "What PlayRef Does For You",
      feature1Title: "Ask in Plain Words",
      feature1Desc: "You don't need to know rule numbers or legal terms. Just describe what happened on the pitch in your own words, and PlayRef understands.",
      feature2Title: "Directly from the Official Rulebook",
      feature2Desc: "Every answer is backed by the official IFAB (International Football Association Board) Laws of the Game. We always show you the exact rule clause so you can see it for yourself.",
      feature3Title: "Explains the 'Why'",
      feature3Desc: "Referee decisions often depend on details (like whether a handball was natural or deliberate). PlayRef explains the different angles referees consider and what would change the call.",
      feature4Title: "Works in 3 Languages",
      feature4Desc: "Chat naturally in English, French, or Arabic with full right-to-left reading support and clean typography.",
      howItWorksTitle: "How to Use PlayRef in 3 Easy Steps",
      step1Title: "1. Ask your question",
      step1Desc: "Type any football situation into the chat bar, or click one of the suggested cards on the home screen.",
      step2Title: "2. Read the simple breakdown",
      step2Desc: "Get a direct explanation of the rule, common interpretations, and what the referee looks for.",
      step3Title: "3. Check the official rule",
      step3Desc: "Click any green rule chip to slide open the exact wording from the official IFAB handbook.",
      refereeNoticeTitle: "A Friendly Note on Refereeing",
      refereeNoticeDesc: "PlayRef is here to help you understand and discuss the rules—it does not replace the match referee! Football happens fast, and human referees judge speed, intent, and intensity on the pitch in real time.",
      ctaButton: "Start Asking Questions",
      browseLawsBtn: "Browse All 17 Laws",
    },
    lawBrowser: "Law Browser",
    newChat: "New Chat",
    recentChats: "Recent Questions",
    noRecentChats: "No previous questions yet",
    suggestedPrompts: [
      {
        title: "Explain offside",
        description: "Deliberate play vs deflection and line of sight",
        prompt: "Explain offside under Law 11, specifically the difference between deliberate play and a deflection.",
      },
      {
        title: "Is deliberate handball always a foul?",
        description: "Natural movement, arm position & deflection rules",
        prompt: "Is a deliberate handball always a direct free kick or penalty, and what exceptions exist?",
      },
      {
        title: "What is DOGSO?",
        description: "Denial of an obvious goal-scoring opportunity & sanctions",
        prompt: "What criteria define DOGSO under Law 12, and when is a red card downgraded to yellow inside the penalty area?",
      },
      {
        title: "Goal from goal kick?",
        description: "Direct scoring rules from restarts",
        prompt: "Can a goalkeeper or player score a goal directly from a goal kick into the opponent's goal or own goal?",
      },
      {
        title: "Advantage rule",
        description: "When referees apply advantage and restart options",
        prompt: "When should the referee apply advantage, and how many seconds do they have to pull play back?",
      },
      {
        title: "Professional foul sanctions",
        description: "Tactical stopping of promising attacks (SPA)",
        prompt: "What counts as Stopping a Promising Attack (SPA) and what disciplinary sanction applies?",
      },
    ],
    stages: {
      routing: "Analyzing intent and language...",
      searching: "Searching official IFAB Laws...",
      checking: "Checking rules & reranking clauses...",
      writing: "Writing grounded explanation...",
    },
    answerCard: {
      shortAnswer: "Short Answer",
      applicableLaws: "Applicable Laws",
      possibleInterpretations: "Possible Interpretations & Discretion",
      whatWouldChange: "What Would Change the Decision",
      assumptions: "Assumptions Made",
      clarifyingDetail: "I need one more detail:",
      submitClarification: "Submit detail",
      orCustomAnswer: "Or provide specific detail...",
      feedbackHelpful: "Helpful",
      feedbackNotHelpful: "Not helpful",
      wrongLawCited: "Wrong law cited",
      feedbackThanks: "Thank you for helping improve PlayRef!",
    },
    citationDrawer: {
      title: "Rule Citation Details",
      officialText: "Official IFAB Text",
      law: "Law",
      page: "Page",
      edition: "Edition",
      source: "Source",
      copyCitation: "Copy citation",
      citationCopied: "Citation copied to clipboard!",
      openInLawBrowser: "Open in Law Browser",
      close: "Close",
    },
    lawBrowserView: {
      title: "IFAB Laws of the Game Explorer",
      searchPlaceholder: "Search 17 Laws or specific terms (e.g. penalty, offside, DOGSO)...",
      allLaws: "All 17 Laws",
      chunksCount: "clauses",
      askAboutSection: "Ask PlayRef about this clause",
      selectLawPrompt: "Select a Law from the sidebar to inspect its official IFAB clauses.",
      loadingLaw: "Loading official Law text...",
      emptySearchResults: "No matching clauses found. Try another term.",
    },
    feedbackModal: {
      title: "Report Incorrect Citation",
      subtitle: "Help us ensure 100% fidelity to the official IFAB Laws.",
      optionWrongLaw: "Wrong Law number cited",
      optionMissingLaw: "Applicable Law clause is missing",
      optionUnclear: "Explanation is unclear or contradictory",
      optionOther: "Other issue",
      commentPlaceholder: "Explain what was incorrect or which Law should have been referenced (optional)...",
      submit: "Submit Report",
      cancel: "Cancel",
    },
    disclaimer: "PlayRef explains official IFAB Laws of the Game and possible interpretations. It does not provide official match verdicts.",
    status: {
      connected: "Laws Database Connected",
      connecting: "Connecting...",
      error: "Backend Disconnected",
      rateLimited: "You are asking quickly. Please wait a moment.",
    },
  },
  fr: {
    appName: "PlayRef",
    tagline: "Assistant des Lois du Jeu de Football",
    homeHeadline: "Posez vos questions sur les Lois du Jeu",
    homeSubline: "Réponses fondées sur les Lois officielles de l'IFAB, avec citations vérifiables.",
    inputPlaceholder: "Décrivez une situation de match ou posez une question sur une Loi...",
    send: "Envoyer",
    stop: "Arrêter",
    about: "À propos",
    aboutView: {
      badge: "Les règles en toute simplicité",
      title: "Qu'est-ce que PlayRef ?",
      subtitle: "Votre compagnon pour comprendre les règles officielles du football. Pas de jargon technique, pas d'approximations : des réponses claires directement issues du règlement officiel de l'IFAB.",
      whatIsPlayRef: "Pourquoi PlayRef existe-t-il ?",
      whatIsPlayRefDesc: "Vous avez déjà débattu entre amis d'un coup de sifflet litigieux ? Vous vous demandez pourquoi un but a été refusé pour une main involontaire, ou si l'on peut marquer directement sur une touche ? Les lois du football peuvent sembler complexes. PlayRef a été créé pour permettre aux supporters, joueurs et entraîneurs de comprendre facilement ce que dit réellement le règlement, en français simple.",
      featuresTitle: "Ce que PlayRef vous apporte",
      feature1Title: "Posez vos questions simplement",
      feature1Desc: "Pas besoin de connaître les numéros d'articles ou le jargon légal. Décrivez simplement l'action avec vos propres mots, et PlayRef vous répond.",
      feature2Title: "Fidèle au règlement officiel",
      feature2Desc: "Chaque réponse s'appuie directement sur les Lois du Jeu officielles de l'IFAB. Nous citons toujours la clause exacte pour que vous puissiez vérifier de vos propres yeux.",
      feature3Title: "Comprendre le pourquoi",
      feature3Desc: "Une décision arbitrale dépend souvent de nuances (mouvement naturel ou délibéré). PlayRef vous explique les critères pris en compte par les arbitres et ce qui peut changer la décision.",
      feature4Title: "Disponible en 3 langues",
      feature4Desc: "Posez vos questions en français, anglais ou arabe, avec une interface fluide et adaptée.",
      howItWorksTitle: "Comment utiliser PlayRef en 3 étapes",
      step1Title: "1. Posez votre question",
      step1Desc: "Écrivez votre situation dans la barre de discussion ou cliquez sur l'un des exemples proposés.",
      step2Title: "2. Lisez l'explication claire",
      step2Desc: "Découvrez la règle applicable, les interprétations possibles et ce qui peut faire basculer la décision.",
      step3Title: "3. Consultez le texte officiel",
      step3Desc: "Cliquez sur n'importe quelle puce verte pour afficher le texte officiel du livret IFAB.",
      refereeNoticeTitle: "Une note amicale sur l'arbitrage",
      refereeNoticeDesc: "PlayRef vous aide à comprendre et discuter des règles, mais ne remplace pas l'arbitre sur le terrain ! Le football va vite, et les arbitres jugent la vitesse, l'angle et l'intensité en direct.",
      ctaButton: "Poser une question",
      browseLawsBtn: "Parcourir les 17 Lois",
    },
    lawBrowser: "Navigateur des Lois",
    newChat: "Nouvelle discussion",
    recentChats: "Questions récentes",
    noRecentChats: "Aucune question précédente",
    suggestedPrompts: [
      {
        title: "Expliquer le hors-jeu",
        description: "Jeu délibéré vs déviation et ligne de mire",
        prompt: "Explique le hors-jeu selon la Loi 11, en particulier la différence entre un geste délibéré et une déviation.",
      },
      {
        title: "La main est-elle toujours faute ?",
        description: "Position naturelle du bras et critères de sanction",
        prompt: "Un contact de la main délibéré entraîne-t-il toujours un coup franc direct ou penalty ?",
      },
      {
        title: "Qu'est-ce que l'annihilation (DOGSO) ?",
        description: "Critères d'occasion nette de but et sanctions",
        prompt: "Quels sont les 4 critères d'une occasion nette de but (DOGSO) selon la Loi 12 et la règle du double châtiment ?",
      },
      {
        title: "But sur coup de pied de but ?",
        description: "Marquer directement sur reprise de jeu",
        prompt: "Un joueur peut-il marquer directement sur un coup de pied de but dans le but adverse ou son propre but ?",
      },
      {
        title: "La règle de l'avantage",
        description: "Quand laisser l'avantage et délai de retour",
        prompt: "Quand l'arbitre doit-il laisser l'avantage et combien de secondes a-t-il pour revenir à la faute ?",
      },
      {
        title: "Attaque prometteuse (SPA)",
        description: "Faute tactique et cartons",
        prompt: "Qu'est-ce qui caractérise l'arrêt d'une attaque prometteuse (SPA) et quelle sanction s'applique ?",
      },
    ],
    stages: {
      routing: "Analyse de la demande et de la langue...",
      searching: "Recherche dans les Lois officielles de l'IFAB...",
      checking: "Vérification des règles et reclassement...",
      writing: "Rédaction de l'explication documentée...",
    },
    answerCard: {
      shortAnswer: "Réponse courte",
      applicableLaws: "Lois applicables",
      possibleInterpretations: "Interprétations possibles et pouvoir d'appréciation",
      whatWouldChange: "Ce qui changerait la décision",
      assumptions: "Hypothèses retenues",
      clarifyingDetail: "J'ai besoin d'une précision :",
      submitClarification: "Envoyer la précision",
      orCustomAnswer: "Ou saisissez votre précision...",
      feedbackHelpful: "Utile",
      feedbackNotHelpful: "Pas utile",
      wrongLawCited: "Loi mal citée",
      feedbackThanks: "Merci pour votre contribution à l'amélioration de PlayRef !",
    },
    citationDrawer: {
      title: "Détails de la citation",
      officialText: "Texte officiel IFAB",
      law: "Loi",
      page: "Page",
      edition: "Édition",
      source: "Source",
      copyCitation: "Copier la citation",
      citationCopied: "Citation copiée dans le presse-papiers !",
      openInLawBrowser: "Ouvrir dans le navigateur des Lois",
      close: "Fermer",
    },
    lawBrowserView: {
      title: "Explorateur des Lois du Jeu IFAB",
      searchPlaceholder: "Rechercher parmi les 17 Lois ou un terme précis (hors-jeu, penalty, main)...",
      allLaws: "Les 17 Lois",
      chunksCount: "articles",
      askAboutSection: "Interroger PlayRef sur cet article",
      selectLawPrompt: "Sélectionnez une Loi dans la liste latérale pour consulter ses articles officiels.",
      loadingLaw: "Chargement du texte officiel...",
      emptySearchResults: "Aucun article trouvé. Essayez un autre mot-clé.",
    },
    feedbackModal: {
      title: "Signaler une citation incorrecte",
      subtitle: "Aidez-nous à garantir l'exactitude absolue des références IFAB.",
      optionWrongLaw: "Mauvais numéro de Loi cité",
      optionMissingLaw: "Loi applicable omise",
      optionUnclear: "Explication confuse ou contradictoire",
      optionOther: "Autre remarque",
      commentPlaceholder: "Précisez l'erreur ou la Loi qui aurait dû s'appliquer (facultatif)...",
      submit: "Envoyer le signalement",
      cancel: "Annuler",
    },
    disclaimer: "PlayRef explique les Lois du Jeu officielles de l'IFAB et les interprétations envisageables. Il ne prend aucune décision arbitrale officielle.",
    status: {
      connected: "Base des Lois connectée",
      connecting: "Connexion en cours...",
      error: "Serveur non joignable",
      rateLimited: "Trop de requêtes rapides. Veuillez patienter un instant.",
    },
  },
  ar: {
    appName: "PlayRef | بلاي ريف",
    tagline: "المساعد الذكي لقوانين كرة القدم",
    homeHeadline: "اسأل أي شيء عن قوانين كرة القدم الرسمية",
    homeSubline: "إجابات معللة وموثقة ومستندة مباشرة إلى نصوص مجلس الاتحاد الدولي لكرة القدم (IFAB).",
    inputPlaceholder: "صف حالة تحكيمية أو اسأل عن قانون (مثلاً: هل يمكن تسجيل هدف مباشرة من ركلة مرمى؟)...",
    send: "إرسال",
    stop: "إيقاف",
    about: "عن بلاي ريف",
    aboutView: {
      badge: "قوانين كرة القدم ببساطة",
      title: "ما هو بلاي ريف (PlayRef)؟",
      subtitle: "دليلك السهل والموثوق لفهم قوانين كرة القدم الرسمية. بدون مصطلحات معقدة أو تعقيد—إجابات واضحة ومباشرة مستندة إلى كتيب مجلس الاتحاد الدولي (IFAB).",
      whatIsPlayRef: "لماذا تم إنشاء بلاي ريف؟",
      whatIsPlayRefDesc: "هل اختلفت يوماً مع أصدقائك حول قرار تحكيمي مثير للجدل؟ هل تساءلت لماذا أُلغي هدف بسبب لمسة يد غير مقصودة، أو هل يمكن تسجيل هدف مباشرة من رمية تماس؟ قوانين كرة القدم قد تبدو معقدة أحياناً. صُمم بلاي ريف لمساعدة الجماهير واللاعبين والمدربين على معرفة ما تنص عليه اللوائح الرسمية بأسلوب بسيط ومفهوم للجميع.",
      featuresTitle: "ماذا يقدم لك بلاي ريف؟",
      feature1Title: "اسأل بكلماتك البسيطة",
      feature1Desc: "لست بحاجة لحفظ أرقام القوانين أو المصطلحات القانونية. صف اللقطة التي حدثت على أرض الملعب بأسلوبك اليومي المعتاد.",
      feature2Title: "مستند مباشرة إلى اللائحة الرسمية",
      feature2Desc: "كل إجابة مدعومة بنص صريح من قوانين اللعبة الرسمية الصادرة عن مجلس (IFAB)، مع رابط مباشر للبند الأصلي لتتأكد بنفسك.",
      feature3Title: "توضيح الأسباب والزوايا المختلفة",
      feature3Desc: "قرارات الحكام تعتمد غالباً على تفاصيل دقيقة (مثل لمسة اليد الطبيعية مقابل المتعمدة). يوضح لك بلاي ريف ما يضعه الحكم في اعتباره وما الذي قد يغير القرار.",
      feature4Title: "يدعم 3 لغات بواجهة كاملة",
      feature4Desc: "تحدث بالعربية أو الإنجليزية أو الفرنسية، مع محاذاة كاملة من اليمين إلى اليسار وخط عربي واضح ومريح للعين.",
      howItWorksTitle: "كيف تستخدم بلاي ريف في 3 خطوات سهلة؟",
      step1Title: "1. اطرح سؤالك",
      step1Desc: "اكتب الحالة التحكيمية في صندوق المحادثة، أو اختر إحدى الحالات المقترحة في الصفحة الرئيسية.",
      step2Title: "2. اقرأ التفسير المبسط",
      step2Desc: "ستحصل على إجابة واضحة تشرح القانون المطبق، والتفسيرات الممكنة، والعوامل المؤثرة.",
      step3Title: "3. طالع النص الرسمي",
      step3Desc: "اضغط على أي بطاقة قانون خضراء لقراءة البند الحرفي المقتبس من الكتيب الرسمي.",
      refereeNoticeTitle: "تنويه ودي بشأن التحكيم",
      refereeNoticeDesc: "بلاي ريف يساعدك على فهم القوانين والنقاش حولها—لكنه لا يحل أبداً محل حكم المباراة! كرة القدم لعبة سريعة وحكام الميدان يقيمون السرعة والقصد وشدة الاحتكاك في جزء من الثانية.",
      ctaButton: "ابدأ بطرح سؤالك الآن",
      browseLawsBtn: "تصفح القوانين الـ 17",
    },
    lawBrowser: "مستعرض القوانين",
    newChat: "محادثة جديدة",
    recentChats: "الأسئلة الأخيرة",
    noRecentChats: "لا توجد أسئلة سابقة",
    suggestedPrompts: [
      {
        title: "شرح التسلل",
        description: "اللعب المتعمد مقابل الارتداد ومجال الرؤية",
        prompt: "اشرح التسلل وفقاً للقانون 11، وبخاصة الفرق بين اللعب المتعمد وارتداد الكرة.",
      },
      {
        title: "لمسة اليد المتعمدة",
        description: "الوضع الطبيعي للجسم والذراع وحالات الاستثناء",
        prompt: "هل كل لمسة يد متعمدة تُعد مخالفة بركلة حرة مباشرة أو ركلة جزاء وما هي الاستثناءات؟",
      },
      {
        title: "حالات منع هدف محقق (DOGSO)",
        description: "معايير الفرصة المحققة والبطاقة الحمراء والصفراء",
        prompt: "ما هي معايير منع فرصة تسجيل هدف محقق (DOGSO) ومتى تُخفف العقوبة إلى بطاقة صفراء داخل المنطقة؟",
      },
      {
        title: "هدف من ركلة مرمى؟",
        description: "شروط التسجيل المباشر من استئناف اللعب",
        prompt: "هل يمكن تسجيل هدف مباشرة من ركلة المرمى في مرمى المنافس أو في مرمى الفريق نفسه؟",
      },
      {
        title: "قاعدة إتاحة الفرصة",
        description: "متى يمنح الحكم الفرصة والمهلة الزمنية للعودة للخطأ",
        prompt: "متى يجب على الحكم إتاحة الفرصة وكم ثانية يملك للعودة واحتساب الخطأ الأصلي؟",
      },
      {
        title: "إيقاف هجمة واعدة (SPA)",
        description: "الأخطاء التكتيكية والإنذارات المستحقة",
        prompt: "ما هي معايير إيقاف هجمة واعدة (SPA) في القانون 12 وما هي العقوبة الانضباطية؟",
      },
    ],
    stages: {
      routing: "تحليل السؤال واللغة...",
      searching: "البحث في القوانين الرسمية للـ IFAB...",
      checking: "مراجعة المواد وإعادة الترتيب...",
      writing: "صياغة الشرح الموثق بالمراجع...",
    },
    answerCard: {
      shortAnswer: "خلاصة الإجابة",
      applicableLaws: "القوانين الواجبة التطبيق",
      possibleInterpretations: "التفسيرات المحتملة وسلطة الحكم التقديرية",
      whatWouldChange: "العوامل التي قد تغيّر القرار",
      assumptions: "الافتراضات المأخوذة بعين الاعتبار",
      clarifyingDetail: "أحتاج إلى تفصيل إضافي:",
      submitClarification: "تأكيد المعلومة",
      orCustomAnswer: "أو اكتب تفصيلاً آخر...",
      feedbackHelpful: "مفيد",
      feedbackNotHelpful: "غير مفيد",
      wrongLawCited: "استشهاد غير دقيق بقانون",
      feedbackThanks: "شكراً لمساهمتك في تحسين دقة بلاي ريف!",
    },
    citationDrawer: {
      title: "تفاصيل الاستشهاد بالقانون",
      officialText: "النص الرسمي المعتمد من IFAB",
      law: "القانون",
      page: "الصفحة",
      edition: "الإصدار",
      source: "المصدر",
      copyCitation: "نسخ الاستشهاد",
      citationCopied: "تم نسخ الاستشهاد بنجاح!",
      openInLawBrowser: "فتح في مستعرض القوانين",
      close: "إغلاق",
    },
    lawBrowserView: {
      title: "مستعرض قوانين اللعبة الرسمية (IFAB)",
      searchPlaceholder: "ابحث في القوانين الـ 17 أو ابحث عن مصطلح (تسلل، جزاء، لمسة يد)...",
      allLaws: "كافة القوانين (17)",
      chunksCount: "فقرة معتمدة",
      askAboutSection: "اسأل بلاي ريف عن هذا البند",
      selectLawPrompt: "اختر قانوناً من القائمة الجانبية لقراءة نصوصه وفقراته الرسمية.",
      loadingLaw: "جارٍ تحميل النص القانوني الرسمي...",
      emptySearchResults: "لم يتم العثور على فقرات مطابقة. جرب مصطلحاً آخر.",
    },
    feedbackModal: {
      title: "الإبلاغ عن عدم دقة الاستشهاد",
      subtitle: "ساعدنا في التحقق من المطابقة التامة لنصوص IFAB الرسمية.",
      optionWrongLaw: "تمت الإشارة إلى رقم قانون خاطئ",
      optionMissingLaw: "تم إغفال قانون أو مادة ذات صلة مباشرة",
      optionUnclear: "التفسير غير واضح أو يحتوي على تناقض",
      optionOther: "ملاحظة أخرى",
      commentPlaceholder: "وضح ما كان غير دقيق أو ما هو القانون الصحيح للحالة (اختياري)...",
      submit: "إرسال البلاغ",
      cancel: "إلغاء",
    },
    disclaimer: "بلاي ريف يشرح قوانين IFAB والتفسيرات التحكيمية الممكنة، ولا يُصدر قرارات رسمية ملزمة للمباريات.",
    status: {
      connected: "قاعدة القوانين متصلة",
      connecting: "جارٍ الاتصال...",
      error: "الخادم غير متصل",
      rateLimited: "إرسال سريع، يرجى الانتظار بضع ثوانٍ.",
    },
  },
};

