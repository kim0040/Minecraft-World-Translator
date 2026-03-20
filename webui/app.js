const STORAGE_KEY = "mc-world-translator-ui-v1";

const FALLBACK_META = {
  style_presets: ["neutral", "casual", "formal", "dcinside"],
  example_paths: { world_dir: "", translate_py_path: "" },
  defaults: {
    batch_size: 40,
    temperature: 0.3,
    backup_suffix: ".bak_translate",
    region_dirs: ["region", "entities", "DIM-1/region", "DIM-1/entities"],
    skip_patterns: ["*.bak_translate"],
    resource_pack_source_lang_files: ["en_us.json", "zh_cn.json"],
  },
};

const TARGET_LANGUAGE_VALUES = {
  ko: "한국어",
  en: "English",
  ja: "日本語",
};

const I18N = {
  ko: {
    brandKicker: "Minecraft World Translator",
    brandTitle: "월드 번역 컨트롤 데스크",
    brandCopy:
      "월드 경로, API 정보, 번역 범위, 리소스팩 옵션을 한 화면에서 정리하고 바로 실행할 수 있습니다. 초보자는 스캔부터, 숙련자는 커스텀 프롬프트까지 한 번에 제어하면 됩니다.",
    heroEyebrow: "Browser Workflow",
    heroTitle: "맵 번역 작업을\n브라우저에서 정돈해서 처리합니다",
    heroText:
      "이 UI는 기존 Python 번역기를 감싸는 로컬 컨트롤 패널입니다. 영어, 한국어, 일본어 인터페이스를 지원하고, 라이트/다크 테마 전환, 진행률 모니터링, 설정 재사용까지 포함합니다.",
    stepOneTitle: "연결",
    stepOneBody: "월드 폴더, translate.py, API 모델을 넣고 안전한 기본값부터 확인합니다.",
    stepTwoTitle: "조정",
    stepTwoBody: "대상 언어, 말투, 번역 범위, 리소스팩 옵션을 목적에 맞게 바꿉니다.",
    stepThreeTitle: "실행",
    stepThreeBody: "스캔 또는 실제 번역을 돌리고, 진행 로그와 결과 리포트를 같은 화면에서 확인합니다.",
    sectionQuickEyebrow: "Quick Guide",
    sectionQuickTitle: "바로 시작하기 전에",
    recommendedBadge: "추천 흐름",
    tipSafeTitle: "먼저 스캔",
    tipSafeBody: "처음 다루는 월드면 `스캔만 실행`으로 후보 텍스트부터 확인하는 편이 안전합니다.",
    tipPromptTitle: "기본은 neutral",
    tipPromptBody: "책, 퍼즐 힌트, 안내문이 중요한 맵은 `neutral` 또는 `formal`이 가장 안정적입니다.",
    tipSecretTitle: "API 키는 세션용",
    tipSecretBody: "API 키는 브라우저 저장소에 남기지 않습니다. 새로고침 후 필요하면 다시 넣으면 됩니다.",
    sectionBasicEyebrow: "Core Setup",
    sectionBasicTitle: "기본 연결 정보",
    fieldWorldDir: "월드 폴더 경로",
    helpWorldDir: "번역할 마인크래프트 월드 폴더를 지정합니다. region/entities/resources.zip이 있는 폴더 기준입니다.",
    fieldReportPath: "리포트 저장 경로",
    helpReportPath: "비워두면 월드 폴더 안 `translation_report.json`을 기본값으로 사용합니다.",
    fieldTranslatePy: "translate.py 경로",
    helpTranslatePy: "기존 API 키, base_url, 모델, 시스템 프롬프트를 상속할 원본 스크립트 경로입니다.",
    fieldInheritTranslatePy: "translate.py 상속",
    helpInheritTranslatePy: "켜면 비어 있는 API 관련 값들을 translate.py에서 자동으로 채웁니다.",
    fieldApiKey: "API 키",
    helpApiKey: "현재 세션에서만 사용합니다. 브라우저 저장소에는 보관하지 않습니다.",
    fieldBaseUrl: "Base URL",
    helpBaseUrl: "프록시 또는 호환 API 엔드포인트가 있으면 입력합니다. 없으면 비워둡니다.",
    fieldModel: "모델 이름",
    helpModel: "예: GPT 계열, 호환 LLM 모델명. translate.py 상속을 쓰면 비워둘 수 있습니다.",
    sectionPromptEyebrow: "Prompt Design",
    sectionPromptTitle: "대상 언어와 스타일",
    fieldTargetLanguage: "대상 언어",
    helpTargetLanguage: "빠른 선택 후 필요하면 커스텀 언어명을 직접 입력할 수 있습니다.",
    fieldCustomLanguage: "커스텀 언어명",
    helpCustomLanguage: "예: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "스타일 프리셋",
    fieldStylePrompt: "추가 스타일 지시",
    helpStylePrompt: "프리셋 뒤에 덧붙일 세부 톤 조정입니다. 말투, 고유명사 처리, 분위기 등을 적습니다.",
    fieldCustomPrompt: "전체 시스템 프롬프트",
    helpCustomPrompt: "이 값을 입력하면 프리셋 대신 완전한 시스템 프롬프트로 사용합니다.",
    sectionScopeEyebrow: "Scan Scope",
    sectionScopeTitle: "무엇을 번역할지",
    scopeSigns: "표지판",
    scopeBooks: "책 페이지",
    scopeCustomNames: "커스텀 이름",
    scopeItemNames: "아이템 이름",
    scopeLore: "Lore",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCommandOutput: "tellraw/title 출력",
    scopeSkipCommands: "실제 명령어 건너뛰기",
    fieldPrefixes: "번역 키 접두사",
    helpPrefixes: "한 줄에 하나씩 넣습니다. `brennenburg.`처럼 translate 키를 텍스트화할 때 씁니다.",
    fieldOverrides: "강제 치환 규칙",
    helpOverrides: "한 줄에 `원문=번역문` 형식으로 넣습니다. 프로젝트 고유 용어 고정용입니다.",
    sectionResourceEyebrow: "Resource Pack",
    sectionResourceTitle: "리소스팩 언어 파일 옵션",
    fieldResourceEnabled: "리소스팩 번역 사용",
    helpResourceEnabled: "resources.zip 같은 lang 파일도 같이 번역합니다.",
    fieldSkipExistingLang: "이미 대상 언어가 있으면 건너뛰기",
    helpSkipExistingLang: "기존 `ko_kr.json` 등을 보존하고 싶을 때 유용합니다.",
    fieldZipPaths: "zip 경로",
    helpZipPaths: "한 줄에 하나씩 입력합니다. 상대 경로는 월드 폴더 기준으로 처리됩니다.",
    fieldSourceLangFiles: "원본 lang 파일명",
    helpSourceLangFiles: "예: en_us.json, zh_cn.json",
    fieldTargetLangFile: "대상 lang 파일명",
    helpTargetLangFile: "예: ko_kr.json, en_us.json, ja_jp.json",
    sectionAdvancedEyebrow: "Advanced",
    sectionAdvancedTitle: "세부 제어",
    fieldBatchSize: "배치 크기",
    helpBatchSize: "한 번에 API로 보내는 문장 수입니다. 응답이 불안하면 낮추는 편이 좋습니다.",
    fieldTemperature: "Temperature",
    helpTemperature: "낮을수록 보수적이고 일관적입니다. 보통 0.1~0.4가 무난합니다.",
    fieldBackupSuffix: "백업 suffix",
    helpBackupSuffix: "원본 백업 파일명 뒤에 붙는 문자열입니다.",
    fieldBackup: "원본 백업",
    helpBackup: "실제 번역 전에 원본 파일을 별도 백업합니다.",
    fieldDryRun: "기본값을 스캔 모드로",
    helpDryRun: "이 체크는 현재 폼 기본값입니다. 아래 버튼으로도 실행 방식을 바로 바꿀 수 있습니다.",
    fieldRegionDirs: "스캔할 region 디렉터리",
    helpRegionDirs: "기본값을 유지하면 일반 월드와 네더/엔티티 영역까지 함께 봅니다.",
    fieldSkipPatterns: "건너뛸 파일 패턴",
    helpSkipPatterns: "예: *.bak_translate",
    actionsTitle: "실행 버튼",
    actionsBody: "스캔은 API 호출 없이 후보만 확인합니다. 실제 번역은 변경 사항을 적용하고 리포트를 남깁니다.",
    actionScan: "스캔만 실행",
    actionTranslate: "실제 번역 실행",
    actionExport: "설정 내보내기",
    actionReset: "기본값 복원",
    monitorEyebrow: "Live Monitor",
    monitorTitle: "실시간 진행 상황",
    timelineEyebrow: "Activity",
    timelineTitle: "작업 로그",
    resultEyebrow: "Report",
    resultTitle: "결과 JSON",
    statPhase: "단계",
    statFiles: "파일 진행",
    statChanged: "수정 파일",
    statCandidates: "후보 파일",
    currentFile: "현재 파일",
    themeLight: "다크 테마로 전환",
    themeDark: "라이트 테마로 전환",
    targetPreset_ko: "한국어",
    targetPreset_en: "영어",
    targetPreset_ja: "일본어",
    targetPreset_custom: "직접 입력",
    stylePreset_neutral: "neutral",
    stylePreset_casual: "casual",
    stylePreset_formal: "formal",
    stylePreset_dcinside: "dcinside",
    stylePresetDesc_neutral: "가장 안전한 기본값입니다. 설명문, 퍼즐 힌트, 시스템 문구에 적합합니다.",
    stylePresetDesc_casual: "조금 더 친근하고 부드럽게 번역합니다. 대사 중심 맵에 어울립니다.",
    stylePresetDesc_formal: "정돈된 문장으로 번역합니다. 안내문, 책, 기록물에 안정적입니다.",
    stylePresetDesc_dcinside: "인터넷 커뮤니티 말투를 섞습니다. 진지한 맵에는 과할 수 있습니다.",
    statusIdle: "대기 중",
    statusQueued: "대기열",
    statusRunning: "실행 중",
    statusCompleted: "완료",
    statusFailed: "실패",
    phaseIdle: "준비 안 됨",
    phaseQueued: "대기",
    phasePreparing: "설정 정리",
    phaseResourcePack: "리소스팩 번역",
    phaseScanPending: "월드 스캔 준비",
    phaseScan: "월드 파일 처리",
    phaseDone: "완료",
    phaseFailed: "실패",
    summaryIdle: "폼을 채운 뒤 스캔 또는 실제 번역을 실행하면 여기서 진행률을 실시간으로 볼 수 있습니다.",
    summaryQueued: "작업을 큐에 올렸습니다. 설정 검증과 초기 준비가 끝나면 바로 실행됩니다.",
    summaryRunning: "월드 파일을 순회하면서 번역 가능한 텍스트를 수집하고 적용하는 중입니다.",
    summaryCompleted: "{changed}개 파일이 수정됐고, 후보 파일은 {candidates}개였습니다.",
    summaryFailed: "작업이 중단됐습니다. 입력 경로나 모델 설정, API 키를 다시 확인하세요.",
    emptyResult: "아직 실행 결과가 없습니다.",
    emptyTimeline: "아직 로그가 없습니다.",
    exportFilename: "translator-config.json",
    eventJobStarted: "작업을 시작했습니다.",
    eventResourcePackStart: "리소스팩 언어 파일 번역을 시작했습니다.",
    eventResourcePackDone: "리소스팩 단계가 끝났습니다. 처리된 zip 결과: {count}",
    eventScanStart: "월드 파일 스캔을 시작했습니다. 대상 파일 수: {total}",
    eventFileStart: "[{index}/{total}] {file} 처리 시작",
    eventFileDone: "[{index}/{total}] {file} 완료 · 수정 청크 {changed} · 후보 텍스트 {candidates}",
    eventDone: "전체 작업 완료. 수정 파일 {changed}, 후보 파일 {candidates}",
    eventCompleted: "번역 리포트를 저장했습니다.",
    eventFailed: "작업 실패: {message}",
    eventUnknown: "이벤트: {event}",
    localScanStarted: "스캔 작업 요청을 서버에 보냈습니다.",
    localTranslateStarted: "실제 번역 작업 요청을 서버에 보냈습니다.",
    localExported: "현재 설정을 JSON 파일로 내보냈습니다.",
    localReset: "폼을 기본값으로 되돌렸습니다.",
    localLoadError: "메타데이터를 불러오지 못해 기본값으로 시작했습니다.",
    localSubmitError: "작업 생성 요청에 실패했습니다: {message}",
  },
  en: {
    brandKicker: "Minecraft World Translator",
    brandTitle: "World Translation Control Desk",
    brandCopy:
      "Configure the world path, API settings, scan scope, and resource-pack options in one place, then run the job directly. Beginners can start with a scan, while advanced users can drive everything with custom prompts.",
    heroEyebrow: "Browser Workflow",
    heroTitle: "Run map translation\nthrough a clean browser dashboard",
    heroText:
      "This UI is a local control panel built around the existing Python translator. It supports English, Korean, and Japanese UI copy, light and dark themes, live progress tracking, and reusable settings.",
    stepOneTitle: "Connect",
    stepOneBody: "Point to the world folder, translate.py, and your model so the tool can inherit safe defaults.",
    stepTwoTitle: "Tune",
    stepTwoBody: "Adjust target language, tone, scan scope, and resource-pack behavior for the map you are working on.",
    stepThreeTitle: "Run",
    stepThreeBody: "Launch a scan or a full translation and review progress logs plus the JSON report in the same screen.",
    sectionQuickEyebrow: "Quick Guide",
    sectionQuickTitle: "Before you start",
    recommendedBadge: "Recommended flow",
    tipSafeTitle: "Scan first",
    tipSafeBody: "If this is a new world, start with scan-only mode so you can review candidates before any write happens.",
    tipPromptTitle: "Use neutral by default",
    tipPromptBody: "For books, puzzle hints, and system text, `neutral` or `formal` is usually the safest choice.",
    tipSecretTitle: "API key stays session-only",
    tipSecretBody: "The API key is not saved in browser storage. If you refresh, enter it again if needed.",
    sectionBasicEyebrow: "Core Setup",
    sectionBasicTitle: "Basic connection settings",
    fieldWorldDir: "World directory",
    helpWorldDir: "Point to the Minecraft world folder that contains region/entities/resources.zip.",
    fieldReportPath: "Report output path",
    helpReportPath: "Leave empty to use `translation_report.json` inside the world folder.",
    fieldTranslatePy: "translate.py path",
    helpTranslatePy: "Path to the legacy script used to inherit API key, base_url, model, and system prompt defaults.",
    fieldInheritTranslatePy: "Inherit from translate.py",
    helpInheritTranslatePy: "When enabled, missing API fields will be filled from translate.py automatically.",
    fieldApiKey: "API key",
    helpApiKey: "Used only for the current session. It is not stored in browser storage.",
    fieldBaseUrl: "Base URL",
    helpBaseUrl: "Set this only if you use a proxy or compatible API endpoint.",
    fieldModel: "Model name",
    helpModel: "Example: a GPT-family or compatible LLM model name. Can stay empty if translate.py provides it.",
    sectionPromptEyebrow: "Prompt Design",
    sectionPromptTitle: "Target language and tone",
    fieldTargetLanguage: "Target language",
    helpTargetLanguage: "Choose a common target first, then switch to a custom label if needed.",
    fieldCustomLanguage: "Custom language label",
    helpCustomLanguage: "Examples: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "Style preset",
    fieldStylePrompt: "Extra style instructions",
    helpStylePrompt: "Use this for finer tone control, name handling, or atmosphere hints.",
    fieldCustomPrompt: "Full system prompt",
    helpCustomPrompt: "If set, this replaces the preset and becomes the full system prompt.",
    sectionScopeEyebrow: "Scan Scope",
    sectionScopeTitle: "What should be translated",
    scopeSigns: "Signs",
    scopeBooks: "Book pages",
    scopeCustomNames: "Custom names",
    scopeItemNames: "Item names",
    scopeLore: "Lore",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCommandOutput: "tellraw/title output",
    scopeSkipCommands: "Skip real commands",
    fieldPrefixes: "Translate key prefixes",
    helpPrefixes: "One per line. Use prefixes like `brennenburg.` when translate keys should become readable text.",
    fieldOverrides: "Forced replacements",
    helpOverrides: "One `source=translation` rule per line for project-specific vocabulary.",
    sectionResourceEyebrow: "Resource Pack",
    sectionResourceTitle: "Language file options",
    fieldResourceEnabled: "Enable resource-pack translation",
    helpResourceEnabled: "Translate `lang/*.json` inside archives such as resources.zip.",
    fieldSkipExistingLang: "Skip if target language already exists",
    helpSkipExistingLang: "Useful when you want to preserve an existing `ko_kr.json` or similar file.",
    fieldZipPaths: "Zip paths",
    helpZipPaths: "One per line. Relative paths are resolved from the world directory.",
    fieldSourceLangFiles: "Source lang filenames",
    helpSourceLangFiles: "Examples: en_us.json, zh_cn.json",
    fieldTargetLangFile: "Target lang filename",
    helpTargetLangFile: "Examples: ko_kr.json, en_us.json, ja_jp.json",
    sectionAdvancedEyebrow: "Advanced",
    sectionAdvancedTitle: "Fine control",
    fieldBatchSize: "Batch size",
    helpBatchSize: "How many strings are sent per API call. Lower it if responses get unstable.",
    fieldTemperature: "Temperature",
    helpTemperature: "Lower values are more conservative and consistent. 0.1 to 0.4 is usually safe.",
    fieldBackupSuffix: "Backup suffix",
    helpBackupSuffix: "Suffix appended to the backup copy before writes happen.",
    fieldBackup: "Create backups",
    helpBackup: "Store original files before any real translation write.",
    fieldDryRun: "Keep form default in scan mode",
    helpDryRun: "This only affects the form default. The action buttons below can still override it instantly.",
    fieldRegionDirs: "Region directories to scan",
    helpRegionDirs: "The default set covers common world, Nether, and entity region folders.",
    fieldSkipPatterns: "Skip patterns",
    helpSkipPatterns: "Example: *.bak_translate",
    actionsTitle: "Run actions",
    actionsBody: "Scan checks candidates without API writes. Full translation applies changes and writes the report.",
    actionScan: "Run Scan Only",
    actionTranslate: "Run Translation",
    actionExport: "Export Settings",
    actionReset: "Reset Defaults",
    monitorEyebrow: "Live Monitor",
    monitorTitle: "Real-time progress",
    timelineEyebrow: "Activity",
    timelineTitle: "Job log",
    resultEyebrow: "Report",
    resultTitle: "Result JSON",
    statPhase: "Phase",
    statFiles: "Files",
    statChanged: "Changed",
    statCandidates: "Candidate files",
    currentFile: "Current file",
    themeLight: "Switch to dark theme",
    themeDark: "Switch to light theme",
    targetPreset_ko: "Korean",
    targetPreset_en: "English",
    targetPreset_ja: "Japanese",
    targetPreset_custom: "Custom",
    stylePreset_neutral: "neutral",
    stylePreset_casual: "casual",
    stylePreset_formal: "formal",
    stylePreset_dcinside: "dcinside",
    stylePresetDesc_neutral: "Safest default for system text, books, hints, and puzzle instructions.",
    stylePresetDesc_casual: "Warmer and more conversational. Good for dialogue-heavy maps.",
    stylePresetDesc_formal: "More structured and restrained. Reliable for notes, books, and records.",
    stylePresetDesc_dcinside: "Uses internet-community tone. It can be too aggressive for serious maps.",
    statusIdle: "Idle",
    statusQueued: "Queued",
    statusRunning: "Running",
    statusCompleted: "Completed",
    statusFailed: "Failed",
    phaseIdle: "Not started",
    phaseQueued: "Queued",
    phasePreparing: "Preparing",
    phaseResourcePack: "Resource pack",
    phaseScanPending: "Ready to scan",
    phaseScan: "Scanning world files",
    phaseDone: "Done",
    phaseFailed: "Failed",
    summaryIdle: "Fill the form and start either a scan or a translation job. Progress will appear here live.",
    summaryQueued: "The job is queued. It will start as soon as validation and setup finish.",
    summaryRunning: "The translator is walking through world files, collecting candidate text, and applying changes.",
    summaryCompleted: "{changed} files were modified, and {candidates} files contained translation candidates.",
    summaryFailed: "The job stopped early. Check paths, model settings, and API credentials.",
    emptyResult: "No result yet.",
    emptyTimeline: "No activity yet.",
    exportFilename: "translator-config.json",
    eventJobStarted: "Job started.",
    eventResourcePackStart: "Started translating resource-pack language files.",
    eventResourcePackDone: "Finished the resource-pack step. Zip results processed: {count}",
    eventScanStart: "Started scanning world files. Target file count: {total}",
    eventFileStart: "[{index}/{total}] Starting {file}",
    eventFileDone: "[{index}/{total}] Finished {file} · changed chunks {changed} · candidate texts {candidates}",
    eventDone: "All work finished. Changed files {changed}, candidate files {candidates}",
    eventCompleted: "Translation report saved.",
    eventFailed: "Job failed: {message}",
    eventUnknown: "Event: {event}",
    localScanStarted: "Submitted a scan-only job to the server.",
    localTranslateStarted: "Submitted a full translation job to the server.",
    localExported: "Exported the current form settings as JSON.",
    localReset: "Restored the form to its default values.",
    localLoadError: "Failed to load metadata. Starting with built-in defaults.",
    localSubmitError: "Failed to create a job: {message}",
  },
  ja: {
    brandKicker: "Minecraft World Translator",
    brandTitle: "ワールド翻訳コントロールデスク",
    brandCopy:
      "ワールドパス、API設定、翻訳範囲、リソースパック設定をひとつの画面で整理して、そのまま実行できます。初回はスキャンから、慣れているならカスタムプロンプトまでまとめて操作できます。",
    heroEyebrow: "Browser Workflow",
    heroTitle: "マップ翻訳を\nブラウザから整理して操作します",
    heroText:
      "このUIは既存のPython翻訳器を包むローカル操作パネルです。英語・韓国語・日本語UI、ライト/ダークテーマ切替、進行状況の監視、設定の再利用に対応しています。",
    stepOneTitle: "接続",
    stepOneBody: "ワールドフォルダ、translate.py、モデル設定を指定して、安全な既定値を読み込みます。",
    stepTwoTitle: "調整",
    stepTwoBody: "対象言語、文体、翻訳範囲、リソースパック設定をマップに合わせて整えます。",
    stepThreeTitle: "実行",
    stepThreeBody: "スキャンまたは本翻訳を開始し、進行ログとJSONレポートを同じ画面で確認します。",
    sectionQuickEyebrow: "Quick Guide",
    sectionQuickTitle: "開始前のポイント",
    recommendedBadge: "推奨フロー",
    tipSafeTitle: "まずはスキャン",
    tipSafeBody: "初めて触るワールドなら、書き込み前に候補だけを確認できるスキャン専用モードが安全です。",
    tipPromptTitle: "最初は neutral",
    tipPromptBody: "本、パズルのヒント、案内文が重要なマップでは `neutral` または `formal` が安定します。",
    tipSecretTitle: "APIキーはセッションのみ",
    tipSecretBody: "APIキーはブラウザ保存領域に残しません。必要なら再読み込み後に入れ直してください。",
    sectionBasicEyebrow: "Core Setup",
    sectionBasicTitle: "基本接続設定",
    fieldWorldDir: "ワールドフォルダ",
    helpWorldDir: "region/entities/resources.zip を含むマインクラフトのワールドフォルダを指定します。",
    fieldReportPath: "レポート保存先",
    helpReportPath: "空欄ならワールドフォルダ内の `translation_report.json` を使います。",
    fieldTranslatePy: "translate.py のパス",
    helpTranslatePy: "APIキー、base_url、モデル、システムプロンプト既定値を継承する元スクリプトです。",
    fieldInheritTranslatePy: "translate.py を継承",
    helpInheritTranslatePy: "有効にすると、空いているAPI関連の値を translate.py から自動補完します。",
    fieldApiKey: "APIキー",
    helpApiKey: "現在のセッションでのみ使用します。ブラウザ保存領域には保存しません。",
    fieldBaseUrl: "Base URL",
    helpBaseUrl: "プロキシや互換APIエンドポイントを使う場合だけ入力します。",
    fieldModel: "モデル名",
    helpModel: "例: GPT系または互換LLMのモデル名。translate.py から継承するなら空欄でも構いません。",
    sectionPromptEyebrow: "Prompt Design",
    sectionPromptTitle: "対象言語とスタイル",
    fieldTargetLanguage: "対象言語",
    helpTargetLanguage: "よく使う候補を選んだあと、必要なら独自の言語名を直接入力できます。",
    fieldCustomLanguage: "カスタム言語名",
    helpCustomLanguage: "例: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "スタイルプリセット",
    fieldStylePrompt: "追加スタイル指示",
    helpStylePrompt: "口調、固有名詞処理、雰囲気などを細かく調整したいときに使います。",
    fieldCustomPrompt: "完全なシステムプロンプト",
    helpCustomPrompt: "入力するとプリセットを無視して、その内容を完全なシステムプロンプトとして使います。",
    sectionScopeEyebrow: "Scan Scope",
    sectionScopeTitle: "何を翻訳するか",
    scopeSigns: "看板",
    scopeBooks: "本のページ",
    scopeCustomNames: "カスタム名",
    scopeItemNames: "アイテム名",
    scopeLore: "Lore",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCommandOutput: "tellraw/title 出力",
    scopeSkipCommands: "実コマンドは除外",
    fieldPrefixes: "翻訳キー接頭辞",
    helpPrefixes: "1行に1つ。`brennenburg.` のような translate キーを可読テキスト化したいときに使います。",
    fieldOverrides: "強制置換ルール",
    helpOverrides: "1行に `原文=翻訳文` 形式で入力します。固有用語の固定に便利です。",
    sectionResourceEyebrow: "Resource Pack",
    sectionResourceTitle: "言語ファイル設定",
    fieldResourceEnabled: "リソースパック翻訳を有効化",
    helpResourceEnabled: "resources.zip などの `lang/*.json` も一緒に翻訳します。",
    fieldSkipExistingLang: "対象言語が既にあればスキップ",
    helpSkipExistingLang: "既存の `ko_kr.json` などを残したい場合に便利です。",
    fieldZipPaths: "zip パス",
    helpZipPaths: "1行に1つ。相対パスはワールドフォルダ基準で解決します。",
    fieldSourceLangFiles: "元の lang ファイル名",
    helpSourceLangFiles: "例: en_us.json, zh_cn.json",
    fieldTargetLangFile: "出力 lang ファイル名",
    helpTargetLangFile: "例: ko_kr.json, en_us.json, ja_jp.json",
    sectionAdvancedEyebrow: "Advanced",
    sectionAdvancedTitle: "詳細制御",
    fieldBatchSize: "バッチサイズ",
    helpBatchSize: "1回のAPI呼び出しで送る文字列数です。不安定なら小さくします。",
    fieldTemperature: "Temperature",
    helpTemperature: "低いほど保守的で一貫します。通常は 0.1 から 0.4 が無難です。",
    fieldBackupSuffix: "バックアップ suffix",
    helpBackupSuffix: "書き込み前のバックアップファイル名の末尾に付く文字列です。",
    fieldBackup: "元ファイルをバックアップ",
    helpBackup: "実翻訳前に元ファイルを別名で保存します。",
    fieldDryRun: "フォーム既定値をスキャンにする",
    helpDryRun: "これはフォームの既定値です。下の実行ボタンでその場で上書きできます。",
    fieldRegionDirs: "走査する region ディレクトリ",
    helpRegionDirs: "既定値のままで通常ワールド、ネザー、entity 領域まで確認できます。",
    fieldSkipPatterns: "除外パターン",
    helpSkipPatterns: "例: *.bak_translate",
    actionsTitle: "実行ボタン",
    actionsBody: "スキャンは候補確認のみ、本翻訳は変更を適用してレポートを書き出します。",
    actionScan: "スキャンのみ実行",
    actionTranslate: "本翻訳を実行",
    actionExport: "設定を書き出す",
    actionReset: "既定値に戻す",
    monitorEyebrow: "Live Monitor",
    monitorTitle: "進行状況",
    timelineEyebrow: "Activity",
    timelineTitle: "ジョブログ",
    resultEyebrow: "Report",
    resultTitle: "結果 JSON",
    statPhase: "段階",
    statFiles: "ファイル進行",
    statChanged: "変更ファイル",
    statCandidates: "候補ファイル",
    currentFile: "現在のファイル",
    themeLight: "ダークテーマへ切替",
    themeDark: "ライトテーマへ切替",
    targetPreset_ko: "韓国語",
    targetPreset_en: "英語",
    targetPreset_ja: "日本語",
    targetPreset_custom: "直接入力",
    stylePreset_neutral: "neutral",
    stylePreset_casual: "casual",
    stylePreset_formal: "formal",
    stylePreset_dcinside: "dcinside",
    stylePresetDesc_neutral: "システム文、本、ヒント、パズル案内に最も安全な既定値です。",
    stylePresetDesc_casual: "やや親しみやすく柔らかい訳になります。会話中心のマップ向けです。",
    stylePresetDesc_formal: "整った文体になります。記録、案内文、本に安定しています。",
    stylePresetDesc_dcinside: "ネットコミュニティ調を混ぜます。真面目なマップには強すぎる場合があります。",
    statusIdle: "待機中",
    statusQueued: "キュー待ち",
    statusRunning: "実行中",
    statusCompleted: "完了",
    statusFailed: "失敗",
    phaseIdle: "未開始",
    phaseQueued: "待機",
    phasePreparing: "準備中",
    phaseResourcePack: "リソースパック",
    phaseScanPending: "スキャン準備",
    phaseScan: "ワールド走査",
    phaseDone: "完了",
    phaseFailed: "失敗",
    summaryIdle: "フォームを入力してスキャンまたは翻訳を開始すると、ここに進行状況がリアルタイムで表示されます。",
    summaryQueued: "ジョブをキューに入れました。検証と初期化が終わり次第すぐに実行されます。",
    summaryRunning: "ワールドファイルを巡回しながら、翻訳候補を集めて変更を適用しています。",
    summaryCompleted: "{changed} 個のファイルが変更され、候補ファイルは {candidates} 個でした。",
    summaryFailed: "ジョブが途中で停止しました。パス、モデル設定、APIキーを再確認してください。",
    emptyResult: "まだ結果がありません。",
    emptyTimeline: "まだログがありません。",
    exportFilename: "translator-config.json",
    eventJobStarted: "ジョブを開始しました。",
    eventResourcePackStart: "リソースパック言語ファイルの翻訳を開始しました。",
    eventResourcePackDone: "リソースパック段階が完了しました。処理した zip 件数: {count}",
    eventScanStart: "ワールドファイルの走査を開始しました。対象ファイル数: {total}",
    eventFileStart: "[{index}/{total}] {file} を開始",
    eventFileDone: "[{index}/{total}] {file} 完了 · 変更チャンク {changed} · 候補テキスト {candidates}",
    eventDone: "全作業が完了しました。変更ファイル {changed}、候補ファイル {candidates}",
    eventCompleted: "翻訳レポートを保存しました。",
    eventFailed: "ジョブ失敗: {message}",
    eventUnknown: "イベント: {event}",
    localScanStarted: "スキャン専用ジョブをサーバーへ送信しました。",
    localTranslateStarted: "本翻訳ジョブをサーバーへ送信しました。",
    localExported: "現在の設定を JSON として書き出しました。",
    localReset: "フォームを既定値に戻しました。",
    localLoadError: "メタデータの取得に失敗したため、内蔵既定値で開始しました。",
    localSubmitError: "ジョブ作成に失敗しました: {message}",
  },
};

const state = {
  lang: localStorage.getItem("mc-world-ui-lang") || "ko",
  theme: localStorage.getItem("mc-world-ui-theme") || "light",
  meta: FALLBACK_META,
  activeJobId: null,
  job: null,
  localEvents: [],
  pollTimer: null,
};

const dom = {};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindDom();
  bindEvents();
  applyTheme();
  applyLanguage();

  try {
    const res = await fetch("/api/meta");
    if (!res.ok) {
      throw new Error(await res.text());
    }
    state.meta = await res.json();
  } catch (error) {
    pushLocalEvent("localLoadError", {}, true);
    state.meta = FALLBACK_META;
  }

  renderStaticOptions();
  populateForm(loadDraft() || buildDefaultDraft());
  renderMonitor();
}

function bindDom() {
  Object.assign(dom, {
    themeToggle: document.getElementById("themeToggle"),
    targetLanguagePreset: document.getElementById("targetLanguagePreset"),
    customLanguageField: document.getElementById("customLanguageField"),
    customLanguage: document.getElementById("customLanguage"),
    stylePreset: document.getElementById("stylePreset"),
    stylePresetHelp: document.getElementById("stylePresetHelp"),
    worldDir: document.getElementById("worldDir"),
    reportPath: document.getElementById("reportPath"),
    translatePyPath: document.getElementById("translatePyPath"),
    inheritTranslatePy: document.getElementById("inheritTranslatePy"),
    apiKey: document.getElementById("apiKey"),
    baseUrl: document.getElementById("baseUrl"),
    model: document.getElementById("model"),
    stylePrompt: document.getElementById("stylePrompt"),
    customSystemPrompt: document.getElementById("customSystemPrompt"),
    translateSigns: document.getElementById("translateSigns"),
    translateBooks: document.getElementById("translateBooks"),
    translateCustomNames: document.getElementById("translateCustomNames"),
    translateItemNames: document.getElementById("translateItemNames"),
    translateLore: document.getElementById("translateLore"),
    translateTitles: document.getElementById("translateTitles"),
    translateFilteredTitles: document.getElementById("translateFilteredTitles"),
    translateCommandOutput: document.getElementById("translateCommandOutput"),
    skipCommandLikeText: document.getElementById("skipCommandLikeText"),
    componentPrefixes: document.getElementById("componentPrefixes"),
    overrides: document.getElementById("overrides"),
    resourceEnabled: document.getElementById("resourceEnabled"),
    zipPaths: document.getElementById("zipPaths"),
    sourceLangFiles: document.getElementById("sourceLangFiles"),
    targetLangFile: document.getElementById("targetLangFile"),
    skipIfTargetExists: document.getElementById("skipIfTargetExists"),
    batchSize: document.getElementById("batchSize"),
    temperature: document.getElementById("temperature"),
    backupSuffix: document.getElementById("backupSuffix"),
    backup: document.getElementById("backup"),
    dryRun: document.getElementById("dryRun"),
    regionDirs: document.getElementById("regionDirs"),
    skipPatterns: document.getElementById("skipPatterns"),
    scanButton: document.getElementById("scanButton"),
    translateButton: document.getElementById("translateButton"),
    exportButton: document.getElementById("exportButton"),
    resetButton: document.getElementById("resetButton"),
    statusPill: document.getElementById("statusPill"),
    monitorSummary: document.getElementById("monitorSummary"),
    progressBar: document.getElementById("progressBar"),
    statPhase: document.getElementById("statPhase"),
    statFiles: document.getElementById("statFiles"),
    statChanged: document.getElementById("statChanged"),
    statCandidates: document.getElementById("statCandidates"),
    currentFile: document.getElementById("currentFile"),
    timeline: document.getElementById("timeline"),
    resultPanel: document.getElementById("resultPanel"),
  });
}

function bindEvents() {
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.addEventListener("click", () => {
      state.lang = button.dataset.langSwitch;
      localStorage.setItem("mc-world-ui-lang", state.lang);
      applyLanguage();
      renderStaticOptions();
      renderMonitor();
    });
  });

  dom.themeToggle.addEventListener("click", () => {
    state.theme = state.theme === "light" ? "dark" : "light";
    localStorage.setItem("mc-world-ui-theme", state.theme);
    applyTheme();
  });

  dom.targetLanguagePreset.addEventListener("change", () => {
    toggleCustomLanguageField();
    persistDraft();
  });

  dom.stylePreset.addEventListener("change", () => {
    updateStyleHelp();
    persistDraft();
  });

  document.getElementById("translatorForm").addEventListener("input", persistDraft);
  document.getElementById("translatorForm").addEventListener("change", persistDraft);

  dom.scanButton.addEventListener("click", () => submitJob(true));
  dom.translateButton.addEventListener("click", () => submitJob(false));
  dom.exportButton.addEventListener("click", exportSettings);
  dom.resetButton.addEventListener("click", resetForm);
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  dom.themeToggle.querySelector(".theme-toggle__label").textContent =
    state.theme === "light" ? t("themeLight") : t("themeDark");
}

function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.classList.toggle("active", button.dataset.langSwitch === state.lang);
  });
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  applyTheme();
}

function buildDefaultDraft() {
  const meta = state.meta || FALLBACK_META;
  return {
    worldDir: meta.example_paths.world_dir || "",
    reportPath: "",
    translatePyPath: meta.example_paths.translate_py_path || "",
    inheritTranslatePy: true,
    apiKey: "",
    baseUrl: "",
    model: "",
    targetLanguagePreset: "ko",
    customLanguage: "",
    stylePreset: "neutral",
    stylePrompt: "",
    customSystemPrompt: "",
    translateSigns: true,
    translateBooks: true,
    translateCustomNames: true,
    translateItemNames: true,
    translateLore: true,
    translateTitles: true,
    translateFilteredTitles: true,
    translateCommandOutput: true,
    skipCommandLikeText: true,
    componentPrefixes: "",
    overrides: "",
    resourceEnabled: false,
    zipPaths: "",
    sourceLangFiles: (meta.defaults.resource_pack_source_lang_files || ["en_us.json", "zh_cn.json"]).join("\n"),
    targetLangFile: "ko_kr.json",
    skipIfTargetExists: false,
    batchSize: meta.defaults.batch_size ?? 40,
    temperature: meta.defaults.temperature ?? 0.3,
    backupSuffix: meta.defaults.backup_suffix || ".bak_translate",
    backup: true,
    dryRun: false,
    regionDirs: (meta.defaults.region_dirs || []).join("\n"),
    skipPatterns: (meta.defaults.skip_patterns || []).join("\n"),
  };
}

function loadDraft() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function persistDraft() {
  const draft = collectDraft();
  draft.apiKey = "";
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
}

function populateForm(draft) {
  dom.worldDir.value = draft.worldDir || "";
  dom.reportPath.value = draft.reportPath || "";
  dom.translatePyPath.value = draft.translatePyPath || "";
  dom.inheritTranslatePy.checked = !!draft.inheritTranslatePy;
  dom.apiKey.value = "";
  dom.baseUrl.value = draft.baseUrl || "";
  dom.model.value = draft.model || "";
  dom.targetLanguagePreset.value = draft.targetLanguagePreset || "ko";
  dom.customLanguage.value = draft.customLanguage || "";
  dom.stylePreset.value = draft.stylePreset || "neutral";
  dom.stylePrompt.value = draft.stylePrompt || "";
  dom.customSystemPrompt.value = draft.customSystemPrompt || "";
  dom.translateSigns.checked = !!draft.translateSigns;
  dom.translateBooks.checked = !!draft.translateBooks;
  dom.translateCustomNames.checked = !!draft.translateCustomNames;
  dom.translateItemNames.checked = !!draft.translateItemNames;
  dom.translateLore.checked = !!draft.translateLore;
  dom.translateTitles.checked = !!draft.translateTitles;
  dom.translateFilteredTitles.checked = !!draft.translateFilteredTitles;
  dom.translateCommandOutput.checked = !!draft.translateCommandOutput;
  dom.skipCommandLikeText.checked = !!draft.skipCommandLikeText;
  dom.componentPrefixes.value = draft.componentPrefixes || "";
  dom.overrides.value = draft.overrides || "";
  dom.resourceEnabled.checked = !!draft.resourceEnabled;
  dom.zipPaths.value = draft.zipPaths || "";
  dom.sourceLangFiles.value = draft.sourceLangFiles || "";
  dom.targetLangFile.value = draft.targetLangFile || "ko_kr.json";
  dom.skipIfTargetExists.checked = !!draft.skipIfTargetExists;
  dom.batchSize.value = draft.batchSize ?? 40;
  dom.temperature.value = draft.temperature ?? 0.3;
  dom.backupSuffix.value = draft.backupSuffix || ".bak_translate";
  dom.backup.checked = !!draft.backup;
  dom.dryRun.checked = !!draft.dryRun;
  dom.regionDirs.value = draft.regionDirs || "";
  dom.skipPatterns.value = draft.skipPatterns || "";
  toggleCustomLanguageField();
  updateStyleHelp();
}

function collectDraft() {
  return {
    worldDir: dom.worldDir.value,
    reportPath: dom.reportPath.value,
    translatePyPath: dom.translatePyPath.value,
    inheritTranslatePy: dom.inheritTranslatePy.checked,
    apiKey: dom.apiKey.value,
    baseUrl: dom.baseUrl.value,
    model: dom.model.value,
    targetLanguagePreset: dom.targetLanguagePreset.value,
    customLanguage: dom.customLanguage.value,
    stylePreset: dom.stylePreset.value,
    stylePrompt: dom.stylePrompt.value,
    customSystemPrompt: dom.customSystemPrompt.value,
    translateSigns: dom.translateSigns.checked,
    translateBooks: dom.translateBooks.checked,
    translateCustomNames: dom.translateCustomNames.checked,
    translateItemNames: dom.translateItemNames.checked,
    translateLore: dom.translateLore.checked,
    translateTitles: dom.translateTitles.checked,
    translateFilteredTitles: dom.translateFilteredTitles.checked,
    translateCommandOutput: dom.translateCommandOutput.checked,
    skipCommandLikeText: dom.skipCommandLikeText.checked,
    componentPrefixes: dom.componentPrefixes.value,
    overrides: dom.overrides.value,
    resourceEnabled: dom.resourceEnabled.checked,
    zipPaths: dom.zipPaths.value,
    sourceLangFiles: dom.sourceLangFiles.value,
    targetLangFile: dom.targetLangFile.value,
    skipIfTargetExists: dom.skipIfTargetExists.checked,
    batchSize: dom.batchSize.value,
    temperature: dom.temperature.value,
    backupSuffix: dom.backupSuffix.value,
    backup: dom.backup.checked,
    dryRun: dom.dryRun.checked,
    regionDirs: dom.regionDirs.value,
    skipPatterns: dom.skipPatterns.value,
  };
}

function renderStaticOptions() {
  renderTargetLanguageOptions();
  renderStylePresetOptions();
  updateStyleHelp();
  toggleCustomLanguageField();
}

function renderTargetLanguageOptions() {
  const current = dom.targetLanguagePreset.value || "ko";
  const options = [
    ["ko", t("targetPreset_ko")],
    ["en", t("targetPreset_en")],
    ["ja", t("targetPreset_ja")],
    ["custom", t("targetPreset_custom")],
  ];
  dom.targetLanguagePreset.innerHTML = options
    .map(([value, label]) => `<option value="${value}">${escapeHtml(label)}</option>`)
    .join("");
  dom.targetLanguagePreset.value = options.some(([value]) => value === current) ? current : "ko";
}

function renderStylePresetOptions() {
  const presets = state.meta.style_presets || FALLBACK_META.style_presets;
  const current = dom.stylePreset.value || "neutral";
  dom.stylePreset.innerHTML = presets
    .map((preset) => `<option value="${preset}">${escapeHtml(t(`stylePreset_${preset}`))}</option>`)
    .join("");
  dom.stylePreset.value = presets.includes(current) ? current : "neutral";
}

function updateStyleHelp() {
  dom.stylePresetHelp.textContent = t(`stylePresetDesc_${dom.stylePreset.value}`);
}

function toggleCustomLanguageField() {
  const custom = dom.targetLanguagePreset.value === "custom";
  dom.customLanguageField.classList.toggle("hidden", !custom);
}

async function submitJob(forceDryRun) {
  const payload = buildPayload(forceDryRun);
  setRunButtonsDisabled(true);

  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: payload }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Request failed");
    }
    state.activeJobId = data.id;
    state.job = data;
    state.localEvents = [];
    pushLocalEvent(forceDryRun ? "localScanStarted" : "localTranslateStarted");
    startPolling();
    renderMonitor();
  } catch (error) {
    pushLocalEvent("localSubmitError", { message: error.message }, true);
    setRunButtonsDisabled(false);
    renderMonitor();
  }
}

function buildPayload(forceDryRun) {
  const draft = collectDraft();
  const targetLanguage =
    draft.targetLanguagePreset === "custom"
      ? (draft.customLanguage || "").trim()
      : TARGET_LANGUAGE_VALUES[draft.targetLanguagePreset] || "한국어";

  return {
    world_dir: draft.worldDir.trim(),
    report_path: draft.reportPath.trim(),
    dry_run: forceDryRun ? true : draft.dryRun,
    backup: draft.backup,
    backup_suffix: draft.backupSuffix.trim(),
    batch_size: Number(draft.batchSize) || 40,
    temperature: Number(draft.temperature) || 0.3,
    inherit_translate_py: draft.inheritTranslatePy,
    translate_py_path: draft.translatePyPath.trim(),
    api: {
      api_key: draft.apiKey.trim(),
      base_url: draft.baseUrl.trim(),
      model: draft.model.trim(),
    },
    prompt: {
      target_language: targetLanguage || "한국어",
      style_preset: draft.stylePreset,
      style_prompt: draft.stylePrompt,
      custom_system_prompt: draft.customSystemPrompt,
    },
    scan: {
      region_dirs: splitLines(draft.regionDirs),
      skip_patterns: splitLines(draft.skipPatterns),
      translate_signs: draft.translateSigns,
      translate_books: draft.translateBooks,
      translate_custom_names: draft.translateCustomNames,
      translate_item_names: draft.translateItemNames,
      translate_lore: draft.translateLore,
      translate_titles: draft.translateTitles,
      translate_filtered_titles: draft.translateFilteredTitles,
      translate_command_output: draft.translateCommandOutput,
      skip_command_like_text: draft.skipCommandLikeText,
      component_translate_key_prefixes: splitLines(draft.componentPrefixes),
      overrides: parseOverrides(draft.overrides),
    },
    resource_pack: {
      enabled: draft.resourceEnabled,
      zip_paths: splitLines(draft.zipPaths),
      source_lang_files: splitLines(draft.sourceLangFiles),
      target_lang_file: draft.targetLangFile.trim(),
      skip_if_target_exists: draft.skipIfTargetExists,
    },
  };
}

function splitLines(text) {
  return String(text || "")
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseOverrides(text) {
  const result = {};
  String(text || "")
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const index = line.indexOf("=");
      if (index === -1) {
        return;
      }
      const key = line.slice(0, index).trim();
      const value = line.slice(index + 1).trim();
      if (key) {
        result[key] = value;
      }
    });
  return result;
}

function startPolling() {
  stopPolling();
  pollJob();
  state.pollTimer = window.setInterval(pollJob, 1200);
}

function stopPolling() {
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

async function pollJob() {
  if (!state.activeJobId) {
    return;
  }
  try {
    const res = await fetch(`/api/jobs/${state.activeJobId}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Polling failed");
    }
    state.job = data;
    if (["completed", "failed"].includes(data.status)) {
      setRunButtonsDisabled(false);
      stopPolling();
    }
    renderMonitor();
  } catch (error) {
    pushLocalEvent("localSubmitError", { message: error.message }, true);
    setRunButtonsDisabled(false);
    stopPolling();
    renderMonitor();
  }
}

function setRunButtonsDisabled(disabled) {
  dom.scanButton.disabled = disabled;
  dom.translateButton.disabled = disabled;
  dom.scanButton.style.opacity = disabled ? "0.6" : "1";
  dom.translateButton.style.opacity = disabled ? "0.6" : "1";
}

function exportSettings() {
  const payload = buildPayload(dom.dryRun.checked);
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = t("exportFilename");
  anchor.click();
  URL.revokeObjectURL(url);
  pushLocalEvent("localExported");
  renderMonitor();
}

function resetForm() {
  populateForm(buildDefaultDraft());
  persistDraft();
  pushLocalEvent("localReset");
  renderMonitor();
}

function pushLocalEvent(key, params = {}, error = false) {
  state.localEvents.unshift({
    timestamp: new Date().toISOString(),
    event: key,
    params,
    error,
  });
  state.localEvents = state.localEvents.slice(0, 20);
}

function renderMonitor() {
  const job = state.job;
  const status = job?.status || "idle";
  const progress = job?.progress || {
    phase: "idle",
    percent: 0,
    processed_files: 0,
    total_files: 0,
    changed_file_count: 0,
    candidate_file_count: 0,
    current_file: "",
  };

  dom.statusPill.textContent = statusLabel(status);
  dom.monitorSummary.textContent = buildSummary(status, progress, job?.error || "");
  dom.progressBar.style.width = `${Math.max(0, Math.min(100, progress.percent || 0))}%`;
  dom.statPhase.textContent = phaseLabel(progress.phase || "idle");
  dom.statFiles.textContent = `${progress.processed_files || 0} / ${progress.total_files || 0}`;
  dom.statChanged.textContent = String(progress.changed_file_count || job?.result?.changed_file_count || 0);
  dom.statCandidates.textContent = String(progress.candidate_file_count || job?.result?.candidate_file_count || 0);
  dom.currentFile.textContent = progress.current_file || "—";
  dom.resultPanel.textContent = job?.result ? JSON.stringify(job.result, null, 2) : t("emptyResult");

  const items = job ? job.events.map((event) => ({ ...event, local: false })) : [];
  const timelineItems = items.length ? items : state.localEvents.map((event) => ({ ...event, local: true }));
  renderTimeline(timelineItems);
}

function renderTimeline(events) {
  if (!events.length) {
    dom.timeline.innerHTML = `<div class="timeline-item"><p>${escapeHtml(t("emptyTimeline"))}</p></div>`;
    return;
  }
  dom.timeline.innerHTML = events
    .slice()
    .reverse()
    .map((event) => {
      const text = event.local ? formatLocalEvent(event) : formatServerEvent(event);
      const klass = event.error || event.event === "job_failed" ? "timeline-item error" : "timeline-item";
      return `
        <div class="${klass}">
          <time>${escapeHtml(formatTime(event.timestamp))}</time>
          <p>${escapeHtml(text)}</p>
        </div>
      `;
    })
    .join("");
}

function formatLocalEvent(event) {
  return formatTemplate(t(event.event), event.params || {});
}

function formatServerEvent(event) {
  switch (event.event) {
    case "job_started":
      return t("eventJobStarted");
    case "resource_pack_start":
      return t("eventResourcePackStart");
    case "resource_pack_done":
      return formatTemplate(t("eventResourcePackDone"), { count: event.count ?? 0 });
    case "scan_start":
      return formatTemplate(t("eventScanStart"), { total: event.total_files ?? 0 });
    case "file_start":
      return formatTemplate(t("eventFileStart"), {
        index: event.index ?? 0,
        total: event.total ?? 0,
        file: baseName(event.file),
      });
    case "file_done":
      return formatTemplate(t("eventFileDone"), {
        index: event.index ?? 0,
        total: event.total ?? 0,
        file: baseName(event.file),
        changed: event.changed_chunks ?? 0,
        candidates: event.candidates ?? 0,
      });
    case "done":
      return formatTemplate(t("eventDone"), {
        changed: event.changed_file_count ?? 0,
        candidates: event.candidate_file_count ?? 0,
      });
    case "job_completed":
      return t("eventCompleted");
    case "job_failed":
      return formatTemplate(t("eventFailed"), { message: event.message || "" });
    default:
      return formatTemplate(t("eventUnknown"), { event: event.event });
  }
}

function statusLabel(status) {
  switch (status) {
    case "queued":
      return t("statusQueued");
    case "running":
      return t("statusRunning");
    case "completed":
      return t("statusCompleted");
    case "failed":
      return t("statusFailed");
    default:
      return t("statusIdle");
  }
}

function phaseLabel(phase) {
  switch (phase) {
    case "queued":
      return t("phaseQueued");
    case "preparing":
      return t("phasePreparing");
    case "resource_pack":
      return t("phaseResourcePack");
    case "scan_pending":
      return t("phaseScanPending");
    case "scan":
      return t("phaseScan");
    case "done":
      return t("phaseDone");
    case "failed":
      return t("phaseFailed");
    default:
      return t("phaseIdle");
  }
}

function buildSummary(status, progress, errorMessage) {
  switch (status) {
    case "queued":
      return t("summaryQueued");
    case "running":
      return t("summaryRunning");
    case "completed":
      return formatTemplate(t("summaryCompleted"), {
        changed: progress.changed_file_count || 0,
        candidates: progress.candidate_file_count || 0,
      });
    case "failed":
      return errorMessage ? `${t("summaryFailed")} ${errorMessage}` : t("summaryFailed");
    default:
      return t("summaryIdle");
  }
}

function t(key) {
  return I18N[state.lang]?.[key] ?? I18N.ko[key] ?? key;
}

function formatTemplate(template, values) {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ""));
}

function formatTime(iso) {
  try {
    return new Intl.DateTimeFormat(state.lang, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

function baseName(path) {
  return String(path || "").split("/").pop() || String(path || "");
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
