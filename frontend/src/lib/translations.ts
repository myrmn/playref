import { LanguageCode } from "./types";

export interface TranslationDictionary {
  appName: string;
  tagline: string;
  homeHeadline: string;
  homeSubline: string;
  inputPlaceholder: string;
  send: string;
  stop: string;
  experimental: string;
  experimentalUploadTooltip: string;
  experimentalHelperText: string;
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
    experimental: "Experimental",
    experimentalUploadTooltip: "Upload match image or short clip (Experimental perception)",
    experimentalHelperText: "Image and video analysis are experimental and cannot make definitive refereeing decisions.",
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
    experimental: "Expérimental",
    experimentalUploadTooltip: "Téléverser une image ou un extrait vidéo (Perception expérimentale)",
    experimentalHelperText: "L'analyse d'images et de vidéos est expérimentale et ne constitue pas une décision officielle.",
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
    experimental: "تجريبي",
    experimentalUploadTooltip: "رفع لقطة أو فيديو قصير (تحليل بصري تجريبي)",
    experimentalHelperText: "التحليل البصري للصور والفيديو ميزة تجريبية ولا يُصدر قرارات تحكيمية قطعية.",
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

