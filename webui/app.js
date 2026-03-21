const STORAGE_KEY = "mc-world-translator-ui-v2";

const FALLBACK_META = {
  providers: [
    { id: "openai", label: "OpenAI", default_base_url: "https://api.openai.com/v1", env_var: "OPENAI_API_KEY" },
    { id: "gemini", label: "Gemini", default_base_url: "https://generativelanguage.googleapis.com/v1beta", env_var: "GEMINI_API_KEY" },
    { id: "anthropic", label: "Anthropic", default_base_url: "https://api.anthropic.com/v1", env_var: "ANTHROPIC_API_KEY" },
    { id: "openrouter", label: "OpenRouter", default_base_url: "https://openrouter.ai/api/v1", env_var: "OPENROUTER_API_KEY" },
    { id: "comet", label: "Comet API", default_base_url: "https://api.cometapi.com/v1", env_var: "COMET_API_KEY" },
    { id: "custom_openai", label: "기타 / Custom (OpenAI 호환)", default_base_url: "https://api.openai.com/v1", env_var: "CUSTOM_OPENAI_API_KEY" },
    { id: "custom_anthropic", label: "기타 / Custom (Anthropic 호환)", default_base_url: "https://api.anthropic.com/v1", env_var: "CUSTOM_ANTHROPIC_API_KEY" },
  ],
  style_presets: ["neutral", "casual", "formal", "polite", "story", "custom"],
  example_paths: { world_dir: "", translate_py_path: "" },
  defaults: {
    provider: "comet",
    batch_size: 40,
    temperature: 0.3,
    backup_suffix: ".bak_translate",
    request_timeout: 120,
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
    brandTitle: "마인크래프트 월드 번역기",
    brandCopy:
      "공급자, 모델, 프롬프트, 범위, 리소스팩, 진행 상태를 한 화면에서 정리합니다. 초반에는 안전하게 스캔하고, 확인이 끝나면 그대로 실번역으로 넘기면 됩니다.",
    heroKicker: "Minecraft Localization",
    heroTitle: "마인크래프트 월드와 모드팩을\n원하는 언어로 완벽하게 번역하세요",
    heroText:
      "단순한 텍스트 번역을 넘어 명령어, NBT 데이터, 그리고 리소스팩까지 안전하게 처리합니다. 다양한 AI를 활용해 고유명사와 말투를 유지하며 몰입감 있는 게임 환경을 만들어보세요.",
    providerCustom: "기타 / Custom",
    fieldCustomFormat: "API 형식",
    optCustomOpenAI: "OpenAI 호환",
    optCustomAnthropic: "Anthropic 호환",
    helpCustomFormat: "지원하려는 API 공식 규격에 맞춰 선택하세요.",
    heroPanelOneTitle: "공급자 선택",
    heroPanelOneBody: "Comet, OpenAI, Gemini, Anthropic, OpenRouter 중 하나를 고르고 기본 URL과 모델을 바로 다룹니다.",
    heroPanelTwoTitle: "빠른 조정",
    heroPanelTwoBody: "짧은 스타일 메모만 적어도 API를 통해 더 실전적인 번역 지시로 확장할 수 있습니다.",
    heroPanelThreeTitle: "실시간 확인",
    heroPanelThreeBody: "파일 수, 텍스트 배치 수, 현재 파일, 마지막 업데이트 시각이 계속 보여서 실제로 돌아가는지 바로 알 수 있습니다.",
    connectionKicker: "Step 1",
    connectionTitle: "연결과 모델",
    connectionCopy: "먼저 공급자와 모델, 경로를 잡습니다. 모델 목록 불러오기를 누르면 현재 공급자 기준으로 사용 가능한 모델을 조회합니다.",
    connectionTag: "필수 구간",
    fieldWorldDir: "월드 폴더 경로",
    helpWorldDir: "region, entities, resources.zip이 들어 있는 월드 폴더를 지정합니다.",
    fieldReportPath: "리포트 저장 경로",
    helpReportPath: "비워두면 월드 내부 `translation_report.json`을 사용합니다.",
    fieldTranslatePy: "translate.py 경로",
    helpTranslatePy: "기존 API 키, base_url, 모델, 시스템 프롬프트를 상속할 원본 파일입니다.",
    fieldInheritTranslatePy: "translate.py 상속",
    helpInheritTranslatePy: "빈 API 설정이 있으면 translate.py 값으로 채웁니다.",
    fieldApiKey: "API 키",
    helpApiKey: "현재 세션에서만 사용하며 브라우저 저장소에는 남기지 않습니다.",
    fieldBaseUrl: "Base URL",
    fieldModel: "모델 이름",
    helpModel: "직접 입력도 가능하고, 아래에서 모델 목록을 불러와 클릭해 넣을 수도 있습니다.",
    fieldTimeout: "요청 제한 시간(초)",
    helpTimeout: "모델 응답이 느린 공급자를 쓸 때 여유 있게 늘릴 수 있습니다.",
    baseUrlHelp: "기본 URL: {url} · 환경변수: {env}",
    actionLoadModels: "모델 목록 불러오기",
    modelCatalogIdle: "아직 모델 목록을 불러오지 않았습니다.",
    modelCatalogLoading: "모델 목록을 불러오는 중입니다...",
    modelCatalogLoaded: "{count}개 모델을 불러왔습니다. 클릭하면 모델 입력칸에 채워집니다.",
    modelCatalogError: "모델 목록 조회 실패: {message}",
    promptKicker: "Step 2",
    promptTitle: "대상 언어와 스타일",
    promptCopy: "짧은 메모에서 시작해도 됩니다. 스타일 보정 버튼이 현재 공급자와 모델을 이용해 더 디테일한 지시문으로 다듬어줍니다.",
    fieldTargetLanguage: "대상 언어",
    helpTargetLanguage: "한국어, 영어, 일본어는 빠르게 선택하고, 필요하면 직접 입력으로 바꿉니다.",
    fieldCustomLanguage: "직접 입력 언어명",
    helpCustomLanguage: "예: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "문체/말투 지정",
    fieldStyleBrief: "추가 지시 (문체, 고유명사 등)",
    helpStyleBrief: "예: 중세 호러풍, 고유명사는 원문 유지, 반말 사용 등",
    assistTitle: "AI 지시문 보정",
    assistBody: "짧게 적은 메모를 실제 게임 번역용 추가 지시문으로 확장합니다.",
    actionImproveStyle: "지시문 구체화",
    assistLoading: "스타일 지시를 보정하는 중입니다...",
    assistDone: "스타일 지시를 추가했습니다.",
    assistError: "스타일 보정 실패: {message}",
    fieldStylePrompt: "추가 스타일 지시",
    helpStylePrompt: "프리셋 뒤에 붙는 세부 지시문입니다. 분위기, 고유명사 처리, 말투 강도 등을 여기에 넣습니다.",
    customPromptToggle: "전체 시스템 프롬프트를 직접 넣고 싶다면 열기",
    fieldCustomPrompt: "전체 시스템 프롬프트",
    helpCustomPrompt: "여기에 값을 넣으면 프리셋과 추가 스타일 지시 대신 이 문장을 그대로 사용합니다.",
    targetPreset_ko: "한국어",
    targetPreset_en: "영어",
    targetPreset_ja: "일본어",
    targetPreset_custom: "직접 입력",
    stylePreset_neutral: "차분함",
    stylePreset_casual: "친근함",
    stylePreset_formal: "격식있음",
    stylePreset_polite: "정중함",
    stylePreset_story: "소설풍",
    stylePreset_custom: "직접 설정",
    stylePresetDesc_neutral: "표준 문체입니다. 책, 퍼즐, 시스템 안내에 가장 안전합니다.",
    stylePresetDesc_casual: "대화형 문체입니다. 조금 더 부드럽고 친근한 번역에 적합합니다.",
    stylePresetDesc_formal: "격식 있는 문체입니다. 기록물, 메모, 고풍스러운 안내문에 어울립니다.",
    stylePresetDesc_polite: "플레이어에게 정중한 존댓말로 친절하게 안내하는 번역입니다.",
    stylePresetDesc_story: "몰입감 있는 이야기나 판타지 세계관에 어울리는 수려한 문체를 사용합니다.",
    stylePresetDesc_custom: "지정된 문체 없이 아래 추가 지시에 작성한 내용만으로 번역 패턴을 제어합니다.",
    scopeKicker: "Step 3",
    scopeTitle: "무엇을 번역할지",
    scopeCopy: "복잡한 체크박스를 줄이고 의미별 그룹으로 묶었습니다. 프리셋 버튼으로 빠르게 시작한 뒤 세부 조정만 하면 됩니다.",
    scopePresetRecommended: "추천 구성",
    scopePresetStory: "스토리 우선",
    scopePresetAll: "전부 켜기",
    scopeGroupCore: "핵심 진행 텍스트",
    scopeGroupItems: "아이템과 이름",
    scopeGroupScripted: "커맨드/연출",
    scopeBooks: "책 페이지",
    scopeSigns: "표지판",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCustomNames: "커스텀 이름",
    scopeItemNames: "아이템 이름",
    scopeLore: "Lore",
    scopeCommandOutput: "tellraw/title 출력",
    scopeSkipCommands: "실제 명령어는 건너뛰기",
    resourceKicker: "Step 4",
    resourceTitle: "리소스팩 언어 파일",
    resourceCopy: "리소스팩 번역이 필요한 경우에만 켭니다. 꺼져 있으면 관련 입력칸은 의미만 보여주고 실제 작업에는 포함되지 않습니다.",
    fieldResourceEnabled: "리소스팩 번역 사용",
    fieldZipPaths: "zip 경로",
    helpZipPaths: "한 줄에 하나씩. 상대 경로는 월드 폴더 기준으로 계산됩니다.",
    fieldSourceLangFiles: "원본 lang 파일명",
    helpSourceLangFiles: "예: en_us.json, zh_cn.json",
    fieldTargetLangFile: "대상 lang 파일명",
    helpTargetLangFile: "예: ko_kr.json, en_us.json, ja_jp.json",
    fieldSkipExistingLang: "이미 대상 언어 파일이 있으면 건너뛰기",
    advancedKicker: "Optional",
    advancedTitle: "세부 제어",
    fieldBatchSize: "배치 크기",
    helpBatchSize: "한 번에 API로 보내는 문자열 수입니다. 실패가 잦으면 줄이세요.",
    fieldTemperature: "Temperature",
    helpTemperature: "낮을수록 보수적이고 일관적입니다. 보통 0.1~0.4가 안전합니다.",
    fieldBackupSuffix: "백업 suffix",
    helpBackupSuffix: "원본 파일 백업명 뒤에 붙는 문자열입니다.",
    fieldBackup: "원본 백업",
    helpBackup: "실번역 전에 원본 파일을 따로 복사합니다.",
    fieldDryRun: "기본값을 스캔 모드로",
    helpDryRun: "버튼으로 언제든 스캔/실번역을 바꿀 수 있지만, 폼 기본값은 이 체크를 따릅니다.",
    fieldCheckpointEnabled: "체크포인트 저장",
    helpCheckpointEnabled: "중간 취소나 오류 뒤에 이어서 하려면 켜두는 편이 좋습니다.",
    fieldContinueOnError: "파일 오류 시 계속 진행",
    helpContinueOnError: "문제가 있는 파일만 건너뛰고 나머지 작업을 계속합니다.",
    fieldCheckpointPath: "체크포인트 경로",
    helpCheckpointPath: "비워두면 월드 폴더 안 `.translation_checkpoint.json`을 사용합니다.",
    fieldBatchRetries: "배치 재시도 횟수",
    helpBatchRetries: "API 오류가 나면 이 횟수만큼 먼저 재시도합니다.",
    fieldWriteRetries: "파일 쓰기 재시도 횟수",
    helpWriteRetries: "쓰기 실패 시 원자적 저장으로 다시 시도합니다.",
    advGroupPerf: "🚀 성능 및 API 튜닝",
    advGroupRecover: "💾 저장 및 오류 복구",
    advGroupDebug: "🛠 테스트 모드",
    advGroupMisc: "기타 설정",
    fieldSkipPatterns: "건너뛸 파일 패턴",
    helpSkipPatterns: "예: *.bak_translate",
    fieldPrefixes: "번역 키 접두사",
    helpPrefixes: "한 줄에 하나씩. translate 키를 텍스트화해서 번역할 때 씁니다.",
    fieldOverrides: "강제 치환 규칙",
    helpOverrides: "한 줄에 `원문=번역문` 형식으로 넣습니다.",
    runKicker: "Step 5",
    runTitle: "실행",
    runCopy: "처음에는 스캔으로 후보만 보고, 문제 없으면 실번역으로 넘어가는 흐름을 권장합니다.",
    actionScan: "스캔만 실행",
    actionTranslate: "실제 번역 실행",
    actionResume: "이전 진행 재개",
    actionCancel: "현재 작업 중지",
    actionExport: "설정 JSON 내보내기",
    actionReset: "폼 기본값 복원",
    liveKicker: "Live Monitor",
    liveTitle: "실행 상태",
    statusIdle: "대기 중",
    statusQueued: "대기열",
    statusRunning: "실행 중",
    statusCompleted: "완료",
    statusCancelled: "중지됨",
    statusFailed: "실패",
    phaseIdle: "준비 안 됨",
    phaseQueued: "대기",
    phasePreparing: "초기 준비",
    phaseResourcePack: "리소스팩 처리",
    phaseScanPending: "월드 스캔 준비",
    phaseScan: "월드 파일 처리",
    phaseTranslate: "문장 번역 중",
    phaseCancelled: "중지됨",
    phaseDone: "완료",
    phaseFailed: "실패",
    activityPreparing: "설정과 입력값을 검증하는 중",
    activityResourcePack: "리소스팩 zip 안 언어 파일을 처리하는 중",
    activityScanStart: "월드 파일 스캔을 시작함",
    activityFileStart: "현재 파일의 텍스트 후보를 모으는 중",
    activityFileDone: "현재 파일 처리를 마침",
    activityBatchStart: "배치 번역 요청을 보내는 중",
    activityBatchDone: "배치 번역 응답을 반영하는 중",
    activityBatchError: "배치 실패 후 더 작은 단위로 재시도 중",
    activityResourcePackSkipped: "이미 처리된 리소스팩을 건너뛰는 중",
    activityCheckpointLoaded: "저장된 진행 상황을 불러오는 중",
    activityFileError: "일부 파일 오류를 기록하고 계속 진행 중",
    activityFileWriteRetry: "파일 저장 재시도 중",
    activityCancelRequested: "중지 요청을 반영하는 중",
    activityCancelled: "작업을 중지했고 체크포인트를 저장함",
    activityDone: "전체 작업을 마침",
    activityFailed: "작업이 중단됨",
    summaryIdle: "아직 실행되지 않았습니다. 스캔 또는 실번역을 시작하면 여기에 현재 상태가 계속 갱신됩니다.",
    summaryQueued: "작업이 큐에 들어갔습니다. 준비가 끝나면 바로 실행합니다.",
    summaryRunning: "현재 파일과 번역 배치를 기준으로 상태를 갱신 중입니다. 마지막 업데이트 시각도 같이 확인하세요.",
    summaryCancelled: "작업이 중지됐습니다. 체크포인트가 남아 있으니 `이전 진행 재개`로 이어갈 수 있습니다.",
    summaryCompleted: "{changed}개 파일이 수정됐고, 후보 파일은 {candidates}개였습니다.",
    summaryFailed: "작업이 중단됐습니다. 경로, 공급자, 모델, API 키를 확인하세요.",
    runHintIdle: "월드 폴더를 먼저 지정한 뒤 `스캔만 실행`으로 안전하게 시작하는 편이 좋습니다.",
    runHintReady: "지금 바로 새 작업을 시작할 수 있습니다. 체크포인트 저장이 켜져 있으면 나중에 이어서 할 수 있습니다.",
    runHintRunning: "현재 작업이 실행 중입니다. 중지가 필요하면 `현재 작업 중지`를 누르면 체크포인트를 저장한 뒤 멈춥니다.",
    runHintResume: "이전 중단 작업을 이어갈 수 있습니다. `이전 진행 재개`를 누르면 저장된 체크포인트부터 다시 시작합니다.",
    runHintCancelled: "작업이 중지된 상태입니다. 설정을 유지한 채 `이전 진행 재개`를 누르면 이어서 진행합니다.",
    runHintFailed: "오류로 멈췄지만 체크포인트가 있으면 이어서 진행할 수 있습니다. 설정을 확인한 뒤 재개를 시도하세요.",
    estScale: "예상 규모:",
    estTime: "예상 시간:",
    statPhase: "단계",
    statFiles: "파일 진행",
    statTexts: "번역 배치 텍스트",
    statChanged: "수정 파일",
    statCandidates: "후보 파일",
    statLastUpdate: "마지막 갱신",
    currentProvider: "현재 공급자",
    currentModel: "현재 모델",
    currentActivity: "현재 동작",
    currentFile: "현재 파일",
    logKicker: "Activity",
    logTitle: "작업 로그",
    resultKicker: "Report",
    resultTitle: "결과 JSON",
    supportKicker: "Support",
    supportTitle: "문의와 오류 제보",
    supportCopy: "초보자 문의도 괜찮습니다. 사용 중 막히는 부분, 설치 문제, API 오류, UI 이상 동작은 아래 메일로 보내주세요.",
    supportLicense: "MIT License",
    emptyResult: "아직 결과가 없습니다.",
    emptyTimeline: "아직 로그가 없습니다.",
    themeLight: "다크 테마로 전환",
    themeDark: "라이트 테마로 전환",
    exportFilename: "translator-config.json",
    localLoadError: "메타데이터를 못 불러와서 내장 기본값으로 시작했습니다.",
    geminiWarning: "무료 티어 Gemini API는 15 RPM 제한이 있습니다. 에러 방지를 위해 RPM 제한을 15, TPM 제한을 100만 이하로 설정하는 것을 권장합니다.",
    fieldRpmLimit: "RPM 제한",
    helpRpmLimit: "분당 최대 요청 수 (비워두면 무제한)",
    fieldTpmLimit: "TPM 제한",
    helpTpmLimit: "분당 최대 처리 토큰 수 (비워두면 무제한)",
    localScanStarted: "스캔 작업을 서버에 요청했습니다.",
    localTranslateStarted: "실번역 작업을 서버에 요청했습니다.",
    localResumeStarted: "체크포인트 재개 작업을 서버에 요청했습니다.",
    localCancelRequested: "현재 작업에 중지 요청을 보냈습니다.",
    localCancelError: "중지 요청 실패: {message}",
    localExported: "현재 폼 설정을 JSON으로 내보냈습니다.",
    localReset: "폼을 기본값으로 되돌렸습니다.",
    localSubmitError: "작업 생성 실패: {message}",
    eventJobStarted: "작업을 시작했습니다.",
    eventResourcePackStart: "리소스팩 번역을 시작했습니다.",
    eventResourcePackDone: "리소스팩 단계가 끝났습니다. 처리 결과 수: {count}",
    eventScanStart: "월드 파일 스캔 시작. 대상 파일 수: {total}",
    eventFileStart: "[{index}/{total}] {file} 처리 시작",
    eventFileDone: "[{index}/{total}] {file} 완료 · 수정 청크 {changed} · 후보 텍스트 {candidates}",
    eventBatchStart: "번역 배치 요청 시작 · 묶음 크기 {count}",
    eventBatchDone: "번역 배치 완료 · 묶음 크기 {count}",
    eventBatchError: "배치 번역 오류 · {message}",
    eventResourcePackSkipped: "이미 처리된 리소스팩 건너뜀 · {file}",
    eventCheckpointLoaded: "체크포인트를 불러왔습니다 · 완료 파일 {files} · 리소스팩 {packs}",
    eventFileError: "파일 오류 기록 · {message}",
    eventWriteRetry: "파일 저장 재시도 · {message}",
    eventCancelRequested: "중지 요청을 보냈습니다.",
    eventCancelled: "작업이 중지됐고 체크포인트가 저장됐습니다.",
    eventFatalError: "치명적 오류 발생 · {message}",
    eventDone: "전체 작업 완료 · 수정 파일 {changed} · 후보 파일 {candidates}",
    eventCompleted: "리포트를 저장했습니다.",
    eventFailed: "작업 실패: {message}",
    eventUnknown: "이벤트: {event}",
    relativeNow: "방금 전",
    relativeSeconds: "{count}초 전",
    relativeMinutes: "{count}분 전",
  },
  en: {
    brandKicker: "Minecraft World Translator",
    brandTitle: "Minecraft World Translator",
    brandCopy:
      "Manage provider, model, prompt, scan scope, resource-pack options, and live execution state in one place. Start with a scan, review it, then move straight into a full translation run.",
    heroKicker: "Minecraft Localization",
    heroTitle: "Flawlessly localize your Minecraft worlds and modpacks",
    heroText:
      "Go beyond simple text translation. Safely process commands, NBT data, and resource packs while retaining their format. Use diverse AI models to preserve proper nouns and tone, creating immersive localized gameplay.",
    providerCustom: "Other / Custom",
    fieldCustomFormat: "API Format",
    optCustomOpenAI: "OpenAI Compatible",
    optCustomAnthropic: "Anthropic Compatible",
    helpCustomFormat: "Select the API format the provider uses.",
    heroPanelOneTitle: "Pick a provider",
    heroPanelOneBody: "Switch between Comet, OpenAI, Gemini, Anthropic, and OpenRouter without manually rewriting the transport layer.",
    heroPanelTwoTitle: "Tune faster",
    heroPanelTwoBody: "Even a short note can be expanded into a more practical translation instruction block through the connected API.",
    heroPanelThreeTitle: "See progress clearly",
    heroPanelThreeBody: "Files, translated batch text counts, current file, and last update time stay visible so you can tell the job is still moving.",
    connectionKicker: "Step 1",
    connectionTitle: "Connection and model",
    connectionCopy: "Set the provider, model, and paths first. The model loader will query the selected provider for available models.",
    connectionTag: "Required",
    fieldWorldDir: "World directory",
    helpWorldDir: "Point to the world folder that contains region, entities, and optionally resources.zip.",
    fieldReportPath: "Report output path",
    helpReportPath: "Leave blank to use `translation_report.json` inside the world folder.",
    fieldTranslatePy: "translate.py path",
    helpTranslatePy: "Legacy file used to inherit API key, base_url, model, and prompt defaults.",
    fieldInheritTranslatePy: "Inherit from translate.py",
    helpInheritTranslatePy: "Missing API settings will be filled from translate.py when available.",
    fieldApiKey: "API key",
    helpApiKey: "Used only for this browser session. It is not written to local storage.",
    fieldBaseUrl: "Base URL",
    fieldModel: "Model name",
    helpModel: "You can type it manually or click a loaded model below to fill this field.",
    fieldTimeout: "Request timeout (sec)",
    helpTimeout: "Increase this if the selected provider or model tends to answer slowly.",
    baseUrlHelp: "Default URL: {url} · env var: {env}",
    actionLoadModels: "Load Available Models",
    modelCatalogIdle: "Model catalog has not been loaded yet.",
    modelCatalogLoading: "Loading model catalog...",
    modelCatalogLoaded: "{count} models loaded. Click one to fill the model field.",
    modelCatalogError: "Model catalog request failed: {message}",
    promptKicker: "Step 2",
    promptTitle: "Target language and tone",
    promptCopy: "A short note is enough to start. The style improver can turn it into a more detailed instruction block using the selected provider and model.",
    fieldTargetLanguage: "Target language",
    helpTargetLanguage: "Pick Korean, English, or Japanese quickly, then switch to custom if needed.",
    fieldCustomLanguage: "Custom language label",
    helpCustomLanguage: "Examples: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "Tone Setting",
    fieldStyleBrief: "Style Notes (Tone, Names)",
    helpStyleBrief: "Example: medieval horror tone, transliterate names, use informal speech",
    assistTitle: "AI Prompt Booster",
    assistBody: "Expand short notes into actionable translation instructions.",
    actionImproveStyle: "Elaborate Instructions",
    assistLoading: "Improving the style instructions...",
    assistDone: "Added the expanded style instructions.",
    assistError: "Style improvement failed: {message}",
    fieldStylePrompt: "Extra style instructions",
    helpStylePrompt: "Appended after the preset. Use this for tone, name handling, puzzle clarity, and pacing.",
    customPromptToggle: "Open this if you want to provide the full system prompt yourself",
    fieldCustomPrompt: "Full system prompt",
    helpCustomPrompt: "If this is filled, it replaces the preset and the extra style prompt.",
    targetPreset_ko: "Korean",
    targetPreset_en: "English",
    targetPreset_ja: "Japanese",
    targetPreset_custom: "Custom",
    stylePreset_neutral: "Neutral",
    stylePreset_casual: "Casual",
    stylePreset_formal: "Formal",
    stylePreset_polite: "Polite",
    stylePreset_story: "Story-driven",
    stylePreset_custom: "Custom",
    stylePresetDesc_neutral: "Standard tone. Safest for books, puzzles, and system guidance.",
    stylePresetDesc_casual: "Conversational tone. Better for softer dialogue.",
    stylePresetDesc_formal: "Formal tone. Stable for records, notes, and old-fashioned exposition.",
    stylePresetDesc_polite: "Uses polite and courteous language to gently guide the player.",
    stylePresetDesc_story: "Uses immersive and dramatic language suitable for fantasy or adventure maps.",
    stylePresetDesc_custom: "Translates exactly as instructed in the extra style instructions below without predefined tone.",
    scopeKicker: "Step 3",
    scopeTitle: "What should be translated",
    scopeCopy: "The scope controls are grouped by meaning instead of being thrown into one flat block. Start from a preset and adjust only what you need.",
    scopePresetRecommended: "Recommended",
    scopePresetStory: "Story-first",
    scopePresetAll: "Enable everything",
    scopeGroupCore: "Core progression text",
    scopeGroupItems: "Items and names",
    scopeGroupScripted: "Commands and effects",
    scopeBooks: "Book pages",
    scopeSigns: "Signs",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCustomNames: "Custom names",
    scopeItemNames: "Item names",
    scopeLore: "Lore",
    scopeCommandOutput: "tellraw/title output",
    scopeSkipCommands: "Skip raw commands",
    resourceKicker: "Step 4",
    resourceTitle: "Resource-pack language files",
    resourceCopy: "Enable this only when you actually need resource-pack translation. When it is off, the section stays readable but does not affect the job.",
    fieldResourceEnabled: "Enable resource-pack translation",
    fieldZipPaths: "Zip paths",
    helpZipPaths: "One path per line. Relative paths resolve from the world directory.",
    fieldSourceLangFiles: "Source lang filenames",
    helpSourceLangFiles: "Examples: en_us.json, zh_cn.json",
    fieldTargetLangFile: "Target lang filename",
    helpTargetLangFile: "Examples: ko_kr.json, en_us.json, ja_jp.json",
    fieldSkipExistingLang: "Skip if target language file already exists",
    advancedKicker: "Optional",
    advancedTitle: "Advanced controls",
    fieldBatchSize: "Batch size",
    helpBatchSize: "How many strings are sent in one API request. Lower it if retries happen often.",
    fieldTemperature: "Temperature",
    helpTemperature: "Lower values are more conservative and consistent. 0.1 to 0.4 is usually safe.",
    fieldBackupSuffix: "Backup suffix",
    helpBackupSuffix: "Text appended to backup filenames before writes happen.",
    fieldBackup: "Create backups",
    helpBackup: "Copy original files before a real translation run writes anything.",
    fieldDryRun: "Keep default in scan mode",
    helpDryRun: "The buttons below still let you switch instantly, but this controls the form default.",
    fieldCheckpointEnabled: "Save checkpoints",
    helpCheckpointEnabled: "Leave this on if you want to stop and resume later.",
    fieldContinueOnError: "Continue after file errors",
    helpContinueOnError: "Skip broken files and keep the rest of the job moving.",
    fieldCheckpointPath: "Checkpoint path",
    helpCheckpointPath: "Leave blank to use `.translation_checkpoint.json` inside the world folder.",
    fieldBatchRetries: "Batch retry count",
    helpBatchRetries: "Retry API failures this many times before splitting batches smaller.",
    fieldWriteRetries: "File write retry count",
    helpWriteRetries: "Retry atomic file writes if the first write fails.",
    advGroupPerf: "🚀 Performance & Tuning",
    advGroupRecover: "💾 Stability & Recovery",
    advGroupDebug: "🛠 Test Mode",
    advGroupMisc: "Misc Settings",
    fieldSkipPatterns: "Skip patterns",
    helpSkipPatterns: "Example: *.bak_translate",
    fieldPrefixes: "Translate key prefixes",
    helpPrefixes: "One per line. Use this when translate keys should become readable text before translation.",
    fieldOverrides: "Forced replacements",
    helpOverrides: "Use one `source=translation` rule per line.",
    runKicker: "Step 5",
    runTitle: "Run",
    runCopy: "A scan-first flow is still recommended. Once the candidate coverage looks right, move to a full translation run.",
    actionScan: "Run Scan Only",
    actionTranslate: "Run Translation",
    actionResume: "Resume Previous Progress",
    actionCancel: "Stop Current Job",
    actionExport: "Export JSON Settings",
    actionReset: "Reset Form",
    liveKicker: "Live Monitor",
    liveTitle: "Execution status",
    statusIdle: "Idle",
    statusQueued: "Queued",
    statusRunning: "Running",
    statusCompleted: "Completed",
    statusCancelled: "Cancelled",
    statusFailed: "Failed",
    phaseIdle: "Not started",
    phaseQueued: "Queued",
    phasePreparing: "Preparing",
    phaseResourcePack: "Resource pack",
    phaseScanPending: "Ready to scan",
    phaseScan: "Scanning world files",
    phaseTranslate: "Translating batches",
    phaseCancelled: "Cancelled",
    phaseDone: "Done",
    phaseFailed: "Failed",
    activityPreparing: "Validating settings and inputs",
    activityResourcePack: "Translating resource-pack language files",
    activityScanStart: "Starting the world-file scan",
    activityFileStart: "Collecting text candidates from the current file",
    activityFileDone: "Finished the current file",
    activityBatchStart: "Sending a translation batch request",
    activityBatchDone: "Applying a finished translation batch",
    activityBatchError: "Retrying with a smaller batch after an error",
    activityResourcePackSkipped: "Skipping a resource pack that was already processed",
    activityCheckpointLoaded: "Loading saved progress from a checkpoint",
    activityFileError: "Recording a file error and continuing",
    activityFileWriteRetry: "Retrying a file write",
    activityCancelRequested: "Applying a stop request",
    activityCancelled: "Stopped the job and saved a checkpoint",
    activityDone: "Finished the full job",
    activityFailed: "The job stopped early",
    summaryIdle: "No job has started yet. Once you run a scan or translation, this panel will keep updating live.",
    summaryQueued: "The job is queued and will start as soon as setup finishes.",
    summaryRunning: "The status is being refreshed from current-file and translation-batch activity. Keep an eye on the last update time as well.",
    summaryCancelled: "The job was stopped. A checkpoint should be available, so you can continue with `Resume Previous Progress`.",
    summaryCompleted: "{changed} files were modified, and {candidates} files contained translation candidates.",
    summaryFailed: "The job stopped early. Check paths, provider settings, model name, and API credentials.",
    runHintIdle: "Pick the world directory first, then start with `Run Scan Only` for the safest first pass.",
    runHintReady: "You can start a new job now. If checkpoint saving is enabled, you can stop and continue later.",
    runHintRunning: "A job is running right now. Use `Stop Current Job` if you need to stop safely and keep a checkpoint.",
    runHintResume: "Previous progress can be resumed. Use `Resume Previous Progress` to continue from the saved checkpoint.",
    runHintCancelled: "The job is stopped. Keep your settings and use `Resume Previous Progress` to continue.",
    runHintFailed: "The job stopped on an error, but you may still be able to continue from a saved checkpoint after fixing the settings.",
    estScale: "Estimated Scale:",
    estTime: "Estimated Time:",
    statPhase: "Phase",
    statFiles: "Files",
    statTexts: "Batch text count",
    statChanged: "Changed files",
    statCandidates: "Candidate files",
    statLastUpdate: "Last update",
    currentProvider: "Current provider",
    currentModel: "Current model",
    currentActivity: "Current activity",
    currentFile: "Current file",
    logKicker: "Activity",
    logTitle: "Job log",
    resultKicker: "Report",
    resultTitle: "Result JSON",
    supportKicker: "Support",
    supportTitle: "Questions and Error Reports",
    supportCopy: "Beginner questions are welcome. If you hit setup problems, API errors, or unexpected UI behavior, send details to the email below.",
    supportLicense: "MIT License",
    emptyResult: "No result yet.",
    emptyTimeline: "No log entries yet.",
    themeLight: "Switch to dark theme",
    themeDark: "Switch to light theme",
    exportFilename: "translator-config.json",
    localLoadError: "Metadata could not be loaded, so the UI started with built-in defaults.",
    geminiWarning: "The free tier of Gemini API has a limit of 15 RPM. We strongly recommend setting RPM limit to 15 and TPM limit below 1,000,000.",
    fieldRpmLimit: "RPM Limit",
    helpRpmLimit: "Max requests per minute.",
    fieldTpmLimit: "TPM Limit",
    helpTpmLimit: "Max generated tokens per minute.",
    localScanStarted: "Submitted a scan job to the server.",
    localTranslateStarted: "Submitted a full translation job to the server.",
    localResumeStarted: "Submitted a resume-from-checkpoint job to the server.",
    localCancelRequested: "Sent a stop request for the current job.",
    localCancelError: "Stop request failed: {message}",
    localExported: "Exported the current form settings as JSON.",
    localReset: "Restored the form to its default values.",
    localSubmitError: "Job creation failed: {message}",
    eventJobStarted: "Job started.",
    eventResourcePackStart: "Started resource-pack translation.",
    eventResourcePackDone: "Finished the resource-pack phase. Result count: {count}",
    eventScanStart: "Started scanning world files. Target files: {total}",
    eventFileStart: "[{index}/{total}] Starting {file}",
    eventFileDone: "[{index}/{total}] Finished {file} · changed chunks {changed} · candidate texts {candidates}",
    eventBatchStart: "Started a translation batch · batch size {count}",
    eventBatchDone: "Finished a translation batch · batch size {count}",
    eventBatchError: "Batch translation error · {message}",
    eventResourcePackSkipped: "Skipped an already-processed resource pack · {file}",
    eventCheckpointLoaded: "Loaded checkpoint data · completed files {files} · resource packs {packs}",
    eventFileError: "Recorded a file error · {message}",
    eventWriteRetry: "Retrying a file write · {message}",
    eventCancelRequested: "Sent a cancellation request.",
    eventCancelled: "The job was cancelled and a checkpoint was saved.",
    eventFatalError: "Fatal error encountered · {message}",
    eventDone: "Job finished · changed files {changed} · candidate files {candidates}",
    eventCompleted: "Saved the report.",
    eventFailed: "Job failed: {message}",
    eventUnknown: "Event: {event}",
    relativeNow: "just now",
    relativeSeconds: "{count}s ago",
    relativeMinutes: "{count}m ago",
  },
  ja: {
    brandKicker: "Minecraft World Translator",
    brandTitle: "マインクラフト ワールド翻訳機",
    brandCopy:
      "供給元、モデル、プロンプト、翻訳範囲、リソースパック設定、進行状況を一画面で管理します。まずはスキャンで確認し、そのまま本翻訳へ進めます。",
    heroKicker: "Minecraft Localization",
    heroTitle: "マインクラフトのワールドとモッドパックを\nお好みの言語へ完璧に翻訳します",
    heroText:
      "単なるテキスト翻訳を超えて、コマンドやNBTデータ、リソースパックまで形式を保ったまま安全に処理します。多様なAIを活用して固有名詞や口調を維持し、没入感のあるゲーム環境を構築しましょう。",
    providerCustom: "その他 / Custom",
    fieldCustomFormat: "API フォーマット",
    optCustomOpenAI: "OpenAI 互換",
    optCustomAnthropic: "Anthropic 互換",
    helpCustomFormat: "プロバイダが使用するAPIフォーマットを選択してください。",
    heroPanelOneTitle: "供給元を選ぶ",
    heroPanelOneBody: "Comet、OpenAI、Gemini、Anthropic、OpenRouterを切り替えても通信形式を手で直す必要がありません。",
    heroPanelTwoTitle: "素早く調整",
    heroPanelTwoBody: "短いメモだけでも、接続中のAPIを使って実運用向けの指示文へ広げられます。",
    heroPanelThreeTitle: "進行が見える",
    heroPanelThreeBody: "ファイル数、翻訳バッチ文字列数、現在のファイル、最終更新時刻が見えるので、本当に動いているかすぐ分かります。",
    connectionKicker: "Step 1",
    connectionTitle: "接続とモデル",
    connectionCopy: "まず供給元、モデル、パスを決めます。モデル一覧読み込みは選択中の供給元へ問い合わせます。",
    connectionTag: "必須",
    fieldWorldDir: "ワールドフォルダ",
    helpWorldDir: "region、entities、resources.zip を含むワールドフォルダを指定します。",
    fieldReportPath: "レポート保存先",
    helpReportPath: "空欄ならワールド内の `translation_report.json` を使います。",
    fieldTranslatePy: "translate.py のパス",
    helpTranslatePy: "APIキー、base_url、モデル、プロンプト既定値を継承する元ファイルです。",
    fieldInheritTranslatePy: "translate.py を継承",
    helpInheritTranslatePy: "空いているAPI設定を translate.py から補完します。",
    fieldApiKey: "APIキー",
    helpApiKey: "現在のセッションでのみ使用し、ブラウザ保存領域には残しません。",
    fieldBaseUrl: "Base URL",
    fieldModel: "モデル名",
    helpModel: "手入力も可能で、下のモデル一覧をクリックして入力欄へ入れることもできます。",
    fieldTimeout: "リクエスト制限時間(秒)",
    helpTimeout: "応答が遅い供給元やモデルを使うときに長めにできます。",
    baseUrlHelp: "既定URL: {url} · 環境変数: {env}",
    actionLoadModels: "利用可能モデルを取得",
    modelCatalogIdle: "まだモデル一覧を読み込んでいません。",
    modelCatalogLoading: "モデル一覧を読み込み中です...",
    modelCatalogLoaded: "{count}件のモデルを読み込みました。クリックするとモデル欄に入ります。",
    modelCatalogError: "モデル一覧取得に失敗しました: {message}",
    promptKicker: "Step 2",
    promptTitle: "対象言語とスタイル",
    promptCopy: "短いメモから始めて構いません。スタイル補強ボタンが選択中の供給元とモデルを使って、より実践的な指示文へ広げます。",
    fieldTargetLanguage: "対象言語",
    helpTargetLanguage: "韓国語、英語、日本語はすぐ選べて、必要なら直接入力へ切り替えられます。",
    fieldCustomLanguage: "直接入力の言語名",
    helpCustomLanguage: "例: 繁體中文, Deutsch, Brazilian Portuguese",
    fieldStylePreset: "トーン・文体指定",
    fieldStyleBrief: "追加指示 (文体、固有名詞等)",
    helpStyleBrief: "例: 中世ホラー風、固有名詞はそのまま、カジュアルな口調",
    assistTitle: "AI指示補強",
    assistBody: "短いメモを実戦向けの翻訳指示へ拡張します。",
    actionImproveStyle: "指示を具体化",
    assistLoading: "スタイル指示を補強中です...",
    assistDone: "補強したスタイル指示を追加しました。",
    assistError: "スタイル補強に失敗しました: {message}",
    fieldStylePrompt: "追加スタイル指示",
    helpStylePrompt: "プリセットの後ろに付く詳細指示です。雰囲気、固有名詞処理、ヒントの明瞭さなどをここで指定します。",
    customPromptToggle: "完全なシステムプロンプトを自分で入れたい場合は開く",
    fieldCustomPrompt: "完全なシステムプロンプト",
    helpCustomPrompt: "ここに値を入れると、プリセットや追加スタイル指示よりこちらが優先されます。",
    targetPreset_ko: "韓国語",
    targetPreset_en: "英語",
    targetPreset_ja: "日本語",
    targetPreset_custom: "直接入力",
    stylePreset_neutral: "標準",
    stylePreset_casual: "カジュアル",
    stylePreset_formal: "フォーマル",
    stylePreset_polite: "丁寧",
    stylePreset_story: "小説風",
    stylePreset_custom: "直接設定(カスタム)",
    stylePresetDesc_neutral: "標準的な文体です。本やパズル、システム案内に最も安全です。",
    stylePresetDesc_casual: "やや柔らかく親しみやすい訳に向きます。",
    stylePresetDesc_formal: "記録やメモ、古風な説明文に適した硬い文体です。",
    stylePresetDesc_polite: "プレイヤーに敬語を使って親切に案内します。",
    stylePresetDesc_story: "ファンタジーやアドベンチャーマップに適した、没入感のある表現を使います。",
    stylePresetDesc_custom: "プリセットを使わず、下の追加指示だけで翻訳パターンを制御します。",
    scopeKicker: "Step 3",
    scopeTitle: "何を翻訳するか",
    scopeCopy: "単なるチェックボックスの塊ではなく、意味ごとに整理しました。まずプリセットを選び、必要な部分だけ微調整すれば済みます。",
    scopePresetRecommended: "推奨構成",
    scopePresetStory: "ストーリー優先",
    scopePresetAll: "全部オン",
    scopeGroupCore: "進行に直結する文",
    scopeGroupItems: "アイテムと名称",
    scopeGroupScripted: "コマンドと演出",
    scopeBooks: "本のページ",
    scopeSigns: "看板",
    scopeTitles: "title",
    scopeFilteredTitles: "filtered_title",
    scopeCustomNames: "カスタム名",
    scopeItemNames: "アイテム名",
    scopeLore: "Lore",
    scopeCommandOutput: "tellraw/title 出力",
    scopeSkipCommands: "生コマンドは除外",
    resourceKicker: "Step 4",
    resourceTitle: "リソースパック言語ファイル",
    resourceCopy: "必要な場合だけ有効にします。無効時も意味は見えますが、実際のジョブには含まれません。",
    fieldResourceEnabled: "リソースパック翻訳を使う",
    fieldZipPaths: "zip パス",
    helpZipPaths: "1行に1つ。相対パスはワールドフォルダ基準です。",
    fieldSourceLangFiles: "元の lang ファイル名",
    helpSourceLangFiles: "例: en_us.json, zh_cn.json",
    fieldTargetLangFile: "出力 lang ファイル名",
    helpTargetLangFile: "例: ko_kr.json, en_us.json, ja_jp.json",
    fieldSkipExistingLang: "対象言語ファイルが既にあればスキップ",
    advancedKicker: "Optional",
    advancedTitle: "詳細制御",
    fieldBatchSize: "バッチサイズ",
    helpBatchSize: "1回のAPIリクエストに入れる文字列数です。失敗が多いなら下げます。",
    fieldTemperature: "Temperature",
    helpTemperature: "低いほど保守的で一貫します。通常は 0.1 から 0.4 が安全です。",
    fieldBackupSuffix: "バックアップ suffix",
    helpBackupSuffix: "書き込み前のバックアップ名に付く文字列です。",
    fieldBackup: "元ファイルをバックアップ",
    helpBackup: "本翻訳の前に元ファイルを別名でコピーします。",
    fieldDryRun: "既定値をスキャンモードにする",
    helpDryRun: "下のボタンで即座に切り替えられますが、フォーム既定値はこの設定に従います。",
    fieldCheckpointEnabled: "チェックポイント保存",
    helpCheckpointEnabled: "途中停止して後で再開したいなら有効のままが安全です。",
    fieldContinueOnError: "ファイルエラー後も継続",
    helpContinueOnError: "壊れたファイルだけ飛ばして残りを続行します。",
    fieldCheckpointPath: "チェックポイント保存先",
    helpCheckpointPath: "空欄ならワールド内の `.translation_checkpoint.json` を使います。",
    fieldBatchRetries: "バッチ再試行回数",
    helpBatchRetries: "API エラー時に小分け前にこの回数だけ再試行します。",
    fieldWriteRetries: "書き込み再試行回数",
    helpWriteRetries: "保存失敗時に原子的書き込みで再試行します。",
    advGroupPerf: "🚀 パフォーマンス調整",
    advGroupRecover: "💾 安定性と回復",
    advGroupDebug: "🛠 テストモード",
    advGroupMisc: "その他の設定",
    fieldSkipPatterns: "除外パターン",
    helpSkipPatterns: "例: *.bak_translate",
    fieldPrefixes: "翻訳キー接頭辞",
    helpPrefixes: "1行に1つ。translate キーを読みやすい文に変換して翻訳したいときに使います。",
    fieldOverrides: "強制置換ルール",
    helpOverrides: "1行に `原文=翻訳文` 形式で入力します。",
    runKicker: "Step 5",
    runTitle: "実行",
    runCopy: "まずはスキャン、問題なければ本翻訳という流れがやはり安全です。",
    actionScan: "スキャンのみ実行",
    actionTranslate: "本翻訳を実行",
    actionResume: "前回の進行を再開",
    actionCancel: "現在の作業を停止",
    actionExport: "設定JSONを書き出す",
    actionReset: "フォームを初期化",
    liveKicker: "Live Monitor",
    liveTitle: "実行状態",
    statusIdle: "待機中",
    statusQueued: "キュー待ち",
    statusRunning: "実行中",
    statusCompleted: "完了",
    statusCancelled: "停止済み",
    statusFailed: "失敗",
    phaseIdle: "未開始",
    phaseQueued: "待機",
    phasePreparing: "準備中",
    phaseResourcePack: "リソースパック",
    phaseScanPending: "スキャン準備",
    phaseScan: "ワールド処理中",
    phaseTranslate: "文の翻訳中",
    phaseCancelled: "停止済み",
    phaseDone: "完了",
    phaseFailed: "失敗",
    activityPreparing: "設定と入力値を検証中",
    activityResourcePack: "リソースパック内の言語ファイルを処理中",
    activityScanStart: "ワールドファイル走査を開始",
    activityFileStart: "現在のファイルから候補文を集めている",
    activityFileDone: "現在のファイルを処理し終えた",
    activityBatchStart: "翻訳バッチ要求を送信中",
    activityBatchDone: "翻訳バッチ結果を反映中",
    activityBatchError: "エラー後に小さいバッチで再試行中",
    activityResourcePackSkipped: "既に処理済みのリソースパックをスキップ中",
    activityCheckpointLoaded: "保存済み進行を読み込み中",
    activityFileError: "ファイルエラーを記録して継続中",
    activityFileWriteRetry: "ファイル保存を再試行中",
    activityCancelRequested: "停止要求を反映中",
    activityCancelled: "作業を止めてチェックポイントを保存した",
    activityDone: "全体作業を完了",
    activityFailed: "ジョブが途中停止",
    summaryIdle: "まだ実行されていません。スキャンか本翻訳を開始すると、このパネルがリアルタイムで更新されます。",
    summaryQueued: "ジョブをキューに入れました。準備が終わり次第すぐに実行されます。",
    summaryRunning: "現在のファイルと翻訳バッチを基準に状態を更新中です。最終更新時刻も併せて確認してください。",
    summaryCancelled: "ジョブは停止しました。チェックポイントが残るので `前回の進行を再開` で続きから実行できます。",
    summaryCompleted: "{changed}個のファイルが変更され、候補ファイルは {candidates} 個でした。",
    summaryFailed: "ジョブが途中で停止しました。パス、供給元、モデル、APIキーを確認してください。",
    runHintIdle: "まずワールドフォルダを指定し、最初は `スキャンのみ実行` から始めるのが安全です。",
    runHintReady: "新しいジョブを開始できます。チェックポイント保存が有効なら途中停止して後で再開できます。",
    runHintRunning: "現在ジョブが動作中です。安全に止めたい場合は `現在の作業を停止` を使ってください。",
    runHintResume: "前回の進行を再開できます。`前回の進行を再開` を押すと保存済みチェックポイントから続行します。",
    runHintCancelled: "ジョブは停止中です。設定を保ったまま `前回の進行を再開` で続きから進められます。",
    runHintFailed: "エラーで停止しましたが、チェックポイントが残っていれば設定修正後に再開できる場合があります。",
    estScale: "予想規模:",
    estTime: "予想時間:",
    statPhase: "段階",
    statFiles: "ファイル進行",
    statTexts: "バッチ文字列数",
    statChanged: "変更ファイル",
    statCandidates: "候補ファイル",
    statLastUpdate: "最終更新",
    currentProvider: "現在の供給元",
    currentModel: "現在のモデル",
    currentActivity: "現在の動作",
    currentFile: "現在のファイル",
    logKicker: "Activity",
    logTitle: "ジョブログ",
    resultKicker: "Report",
    resultTitle: "結果 JSON",
    supportKicker: "Support",
    supportTitle: "問い合わせとエラー報告",
    supportCopy: "初心者の質問でも大丈夫です。セットアップ、API エラー、UI の不具合などは下のメールへ送ってください。",
    supportLicense: "MIT License",
    emptyResult: "まだ結果がありません。",
    emptyTimeline: "まだログがありません。",
    themeLight: "ダークテーマへ切替",
    themeDark: "ライトテーマへ切替",
    exportFilename: "translator-config.json",
    localLoadError: "メタデータ取得に失敗したため、内蔵既定値で開始しました。",
    geminiWarning: "無料利用枠のGemini APIは15RPMの制限があります。エラーを防ぐため、RPM制限を15、TPM制限を100万以下に設定することを強くお勧めします。",
    fieldRpmLimit: "RPM制限",
    helpRpmLimit: "1分あたりの最大リクエスト数",
    fieldTpmLimit: "TPM制限",
    helpTpmLimit: "1分あたりの最大トークン数",
    localScanStarted: "スキャンジョブをサーバーへ送信しました。",
    localTranslateStarted: "本翻訳ジョブをサーバーへ送信しました。",
    localResumeStarted: "チェックポイント再開ジョブをサーバーへ送信しました。",
    localCancelRequested: "現在のジョブへ停止要求を送りました。",
    localCancelError: "停止要求失敗: {message}",
    localExported: "現在のフォーム設定を JSON として書き出しました。",
    localReset: "フォームを既定値に戻しました。",
    localSubmitError: "ジョブ作成失敗: {message}",
    eventJobStarted: "ジョブを開始しました。",
    eventResourcePackStart: "リソースパック翻訳を開始しました。",
    eventResourcePackDone: "リソースパック段階が終了しました。結果数: {count}",
    eventScanStart: "ワールドファイル走査開始。対象ファイル数: {total}",
    eventFileStart: "[{index}/{total}] {file} を開始",
    eventFileDone: "[{index}/{total}] {file} 完了 · 変更チャンク {changed} · 候補テキスト {candidates}",
    eventBatchStart: "翻訳バッチ開始 · バッチサイズ {count}",
    eventBatchDone: "翻訳バッチ完了 · バッチサイズ {count}",
    eventBatchError: "バッチ翻訳エラー · {message}",
    eventResourcePackSkipped: "既に処理済みのリソースパックをスキップ · {file}",
    eventCheckpointLoaded: "チェックポイント読込完了 · 完了ファイル {files} · リソースパック {packs}",
    eventFileError: "ファイルエラー記録 · {message}",
    eventWriteRetry: "ファイル保存再試行 · {message}",
    eventCancelRequested: "停止要求を送りました。",
    eventCancelled: "ジョブを停止し、チェックポイントを保存しました。",
    eventFatalError: "致命的エラー発生 · {message}",
    eventDone: "全体完了 · 変更ファイル {changed} · 候補ファイル {candidates}",
    eventCompleted: "レポートを保存しました。",
    eventFailed: "ジョブ失敗: {message}",
    eventUnknown: "イベント: {event}",
    relativeNow: "たった今",
    relativeSeconds: "{count}秒前",
    relativeMinutes: "{count}分前",
  },
};

const state = {
  lang: localStorage.getItem("mc-world-ui-lang") || "ko",
  theme: localStorage.getItem("mc-world-ui-theme") || "light",
  meta: FALLBACK_META,
  draft: null,
  modelCatalog: [],
  activeJobId: null,
  job: null,
  localEvents: [],
  pollTimer: null,
  renderTimer: null,
};

const dom = {};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindDom();
  bindEvents();
  applyLanguage();
  applyTheme();

  try {
    const response = await fetch("/api/meta");
    if (!response.ok) {
      throw new Error(await response.text());
    }
    state.meta = await response.json();
  } catch {
    state.meta = FALLBACK_META;
    pushLocalEvent("localLoadError", {}, true);
  }

  const draft = loadDraft() || buildDefaultDraft();
  state.draft = draft;
  renderStaticUi();
  populateForm(draft);
  renderMonitor();
  state.renderTimer = window.setInterval(() => renderMonitor(), 1000);
}

function bindDom() {
  Object.assign(dom, {
    themeToggle: document.getElementById("themeToggle"),
    providerPicker: document.getElementById("providerPicker"),
    geminiWarning: document.getElementById("geminiWarning"),
    customProviderSettings: document.getElementById("customProviderSettings"),
    customProviderFormat: document.getElementById("customProviderFormat"),
    worldDir: document.getElementById("worldDir"),
    reportPath: document.getElementById("reportPath"),
    translatePyPath: document.getElementById("translatePyPath"),
    inheritTranslatePy: document.getElementById("inheritTranslatePy"),
    apiKey: document.getElementById("apiKey"),
    baseUrl: document.getElementById("baseUrl"),
    baseUrlHelp: document.getElementById("baseUrlHelp"),
    model: document.getElementById("model"),
    requestTimeout: document.getElementById("requestTimeout"),
    loadModelsButton: document.getElementById("loadModelsButton"),
    modelCatalogStatus: document.getElementById("modelCatalogStatus"),
    modelCatalog: document.getElementById("modelCatalog"),
    targetLanguagePreset: document.getElementById("targetLanguagePreset"),
    customLanguageField: document.getElementById("customLanguageField"),
    customLanguage: document.getElementById("customLanguage"),
    stylePreset: document.getElementById("stylePreset"),
    stylePresetHelp: document.getElementById("stylePresetHelp"),
    styleBrief: document.getElementById("styleBrief"),
    improveStyleButton: document.getElementById("improveStyleButton"),
    styleAssistStatus: document.getElementById("styleAssistStatus"),
    stylePrompt: document.getElementById("stylePrompt"),
    customSystemPrompt: document.getElementById("customSystemPrompt"),
    translateBooks: document.getElementById("translateBooks"),
    translateSigns: document.getElementById("translateSigns"),
    translateTitles: document.getElementById("translateTitles"),
    translateFilteredTitles: document.getElementById("translateFilteredTitles"),
    translateCustomNames: document.getElementById("translateCustomNames"),
    translateItemNames: document.getElementById("translateItemNames"),
    translateLore: document.getElementById("translateLore"),
    translateCommandOutput: document.getElementById("translateCommandOutput"),
    skipCommandLikeText: document.getElementById("skipCommandLikeText"),
    resourceEnabled: document.getElementById("resourceEnabled"),
    resourcePanel: document.getElementById("resourcePanel"),
    zipPaths: document.getElementById("zipPaths"),
    sourceLangFiles: document.getElementById("sourceLangFiles"),
    targetLangFile: document.getElementById("targetLangFile"),
    skipIfTargetExists: document.getElementById("skipIfTargetExists"),
    batchSize: document.getElementById("batchSize"),
    temperature: document.getElementById("temperature"),
    rpmLimit: document.getElementById("rpmLimit"),
    tpmLimit: document.getElementById("tpmLimit"),
    backupSuffix: document.getElementById("backupSuffix"),
    backup: document.getElementById("backup"),
    dryRun: document.getElementById("dryRun"),
    checkpointEnabled: document.getElementById("checkpointEnabled"),
    continueOnFileError: document.getElementById("continueOnFileError"),
    checkpointPath: document.getElementById("checkpointPath"),
    maxBatchRetries: document.getElementById("maxBatchRetries"),
    maxFileWriteRetries: document.getElementById("maxFileWriteRetries"),
    skipPatterns: document.getElementById("skipPatterns"),
    componentPrefixes: document.getElementById("componentPrefixes"),
    overrides: document.getElementById("overrides"),
    scanButton: document.getElementById("scanButton"),
    translateButton: document.getElementById("translateButton"),
    resumeButton: document.getElementById("resumeButton"),
    cancelButton: document.getElementById("cancelButton"),
    exportButton: document.getElementById("exportButton"),
    resetButton: document.getElementById("resetButton"),
    runHint: document.getElementById("runHint"),
    estScale: document.getElementById("estScale"),
    estTime: document.getElementById("estTime"),
    statusPill: document.getElementById("statusPill"),
    livePulse: document.getElementById("livePulse"),
    progressNumber: document.getElementById("progressNumber"),
    progressBar: document.getElementById("progressBar"),
    monitorSummary: document.getElementById("monitorSummary"),
    statPhase: document.getElementById("statPhase"),
    statFiles: document.getElementById("statFiles"),
    statTexts: document.getElementById("statTexts"),
    statChanged: document.getElementById("statChanged"),
    statCandidates: document.getElementById("statCandidates"),
    statLastUpdate: document.getElementById("statLastUpdate"),
    currentProvider: document.getElementById("currentProvider"),
    currentModel: document.getElementById("currentModel"),
    currentActivity: document.getElementById("currentActivity"),
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
      renderStaticUi();
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
    updateStylePresetHelp();
    persistDraft();
  });

  dom.resourceEnabled.addEventListener("change", () => {
    toggleResourcePanel();
    persistDraft();
  });

  dom.customProviderFormat.addEventListener("change", (e) => {
    state.draft.provider = e.target.value;
    persistDraft();
    updateBaseUrlHelp();
  });

  dom.loadModelsButton.addEventListener("click", loadModels);
  dom.improveStyleButton.addEventListener("click", improveStylePrompt);

  document.querySelectorAll("[data-scope-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      applyScopePreset(button.dataset.scopePreset);
      persistDraft();
    });
  });

  [
    dom.worldDir,
    dom.reportPath,
    dom.translatePyPath,
    dom.inheritTranslatePy,
    dom.apiKey,
    dom.baseUrl,
    dom.model,
    dom.requestTimeout,
    dom.customLanguage,
    dom.styleBrief,
    dom.stylePrompt,
    dom.customSystemPrompt,
    dom.translateBooks,
    dom.translateSigns,
    dom.translateTitles,
    dom.translateFilteredTitles,
    dom.translateCustomNames,
    dom.translateItemNames,
    dom.translateLore,
    dom.translateCommandOutput,
    dom.skipCommandLikeText,
    dom.zipPaths,
    dom.sourceLangFiles,
    dom.targetLangFile,
    dom.skipIfTargetExists,
    dom.batchSize,
    dom.temperature,
    dom.rpmLimit,
    dom.tpmLimit,
    dom.backupSuffix,
    dom.backup,
    dom.dryRun,
    dom.checkpointEnabled,
    dom.continueOnFileError,
    dom.checkpointPath,
    dom.maxBatchRetries,
    dom.maxFileWriteRetries,
    dom.skipPatterns,
    dom.componentPrefixes,
    dom.overrides,
  ].forEach((element) => {
    element.addEventListener("input", persistDraft);
    element.addEventListener("change", persistDraft);
  });

  dom.scanButton.addEventListener("click", () => submitJob(true));
  dom.translateButton.addEventListener("click", () => submitJob(false));
  dom.resumeButton.addEventListener("click", resumeJob);
  dom.cancelButton.addEventListener("click", cancelJob);
  dom.exportButton.addEventListener("click", exportSettings);
  dom.resetButton.addEventListener("click", resetForm);
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  dom.themeToggle.textContent = state.theme === "light" ? t("themeLight") : t("themeDark");
}

function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.classList.toggle("active", button.dataset.langSwitch === state.lang);
  });
}

function renderStaticUi() {
  applyLanguage();
  applyTheme();
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  renderProviderPicker();
  renderTargetLanguageOptions();
  renderStylePresetOptions();
  updateStylePresetHelp();
  updateBaseUrlHelp();
  toggleCustomLanguageField();
  toggleResourcePanel();
  renderModelCatalog();
}

function buildDefaultDraft() {
  const meta = state.meta || FALLBACK_META;
  return {
    provider: meta.defaults.provider || "comet",
    worldDir: meta.example_paths.world_dir || "",
    reportPath: "",
    translatePyPath: meta.example_paths.translate_py_path || "",
    inheritTranslatePy: true,
    apiKey: "",
    baseUrl: providerDefaultUrl(meta.defaults.provider || "comet"),
    model: "",
    requestTimeout: meta.defaults.request_timeout || 120,
    targetLanguagePreset: "ko",
    customLanguage: "",
    stylePreset: "neutral",
    styleBrief: "",
    stylePrompt: "",
    customSystemPrompt: "",
    translateBooks: true,
    translateSigns: true,
    translateTitles: true,
    translateFilteredTitles: true,
    translateCustomNames: true,
    translateItemNames: true,
    translateLore: true,
    translateCommandOutput: true,
    skipCommandLikeText: true,
    resourceEnabled: false,
    zipPaths: "",
    sourceLangFiles: (meta.defaults.resource_pack_source_lang_files || ["en_us.json", "zh_cn.json"]).join("\n"),
    targetLangFile: "ko_kr.json",
    skipIfTargetExists: false,
    batchSize: meta.defaults.batch_size || 40,
    temperature: meta.defaults.temperature || 0.3,
    rpmLimit: "",
    tpmLimit: "",
    backupSuffix: meta.defaults.backup_suffix || ".bak_translate",
    backup: true,
    dryRun: false,
    checkpointEnabled: meta.defaults.checkpoint_enabled ?? true,
    continueOnFileError: meta.defaults.continue_on_file_error ?? true,
    checkpointPath: "",
    maxBatchRetries: meta.defaults.max_batch_retries ?? 3,
    maxFileWriteRetries: meta.defaults.max_file_write_retries ?? 2,
    skipPatterns: (meta.defaults.skip_patterns || []).join("\n"),
    componentPrefixes: "",
    overrides: "",
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
  state.draft = collectDraft();
  const stored = { ...state.draft, apiKey: "" };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
}

function collectDraft() {
  return {
    provider: state.draft?.provider || providerFromPicker(),
    worldDir: dom.worldDir.value,
    reportPath: dom.reportPath.value,
    translatePyPath: dom.translatePyPath.value,
    inheritTranslatePy: dom.inheritTranslatePy.checked,
    apiKey: dom.apiKey.value,
    baseUrl: dom.baseUrl.value,
    model: dom.model.value,
    requestTimeout: dom.requestTimeout.value,
    targetLanguagePreset: dom.targetLanguagePreset.value,
    customLanguage: dom.customLanguage.value,
    stylePreset: dom.stylePreset.value,
    styleBrief: dom.styleBrief.value,
    stylePrompt: dom.stylePrompt.value,
    customSystemPrompt: dom.customSystemPrompt.value,
    translateBooks: dom.translateBooks.checked,
    translateSigns: dom.translateSigns.checked,
    translateTitles: dom.translateTitles.checked,
    translateFilteredTitles: dom.translateFilteredTitles.checked,
    translateCustomNames: dom.translateCustomNames.checked,
    translateItemNames: dom.translateItemNames.checked,
    translateLore: dom.translateLore.checked,
    translateCommandOutput: dom.translateCommandOutput.checked,
    skipCommandLikeText: dom.skipCommandLikeText.checked,
    resourceEnabled: dom.resourceEnabled.checked,
    zipPaths: dom.zipPaths.value,
    sourceLangFiles: dom.sourceLangFiles.value,
    targetLangFile: dom.targetLangFile.value,
    skipIfTargetExists: dom.skipIfTargetExists.checked,
    batchSize: dom.batchSize.value,
    temperature: dom.temperature.value,
    rpmLimit: dom.rpmLimit.value,
    tpmLimit: dom.tpmLimit.value,
    backupSuffix: dom.backupSuffix.value,
    backup: dom.backup.checked,
    dryRun: dom.dryRun.checked,
    checkpointEnabled: dom.checkpointEnabled.checked,
    continueOnFileError: dom.continueOnFileError.checked,
    checkpointPath: dom.checkpointPath.value,
    maxBatchRetries: dom.maxBatchRetries.value,
    maxFileWriteRetries: dom.maxFileWriteRetries.value,
    skipPatterns: dom.skipPatterns.value,
    componentPrefixes: dom.componentPrefixes.value,
    overrides: dom.overrides.value,
  };
}

function populateForm(draft) {
  state.draft = { ...buildDefaultDraft(), ...draft };
  dom.worldDir.value = state.draft.worldDir || "";
  dom.reportPath.value = state.draft.reportPath || "";
  dom.translatePyPath.value = state.draft.translatePyPath || "";
  dom.inheritTranslatePy.checked = !!state.draft.inheritTranslatePy;
  dom.apiKey.value = "";
  dom.baseUrl.value = state.draft.baseUrl || providerDefaultUrl(state.draft.provider);
  dom.model.value = state.draft.model || "";
  dom.requestTimeout.value = state.draft.requestTimeout || 120;
  dom.targetLanguagePreset.value = state.draft.targetLanguagePreset || "ko";
  dom.customLanguage.value = state.draft.customLanguage || "";
  dom.stylePreset.value = state.draft.stylePreset || "neutral";
  dom.styleBrief.value = state.draft.styleBrief || "";
  dom.stylePrompt.value = state.draft.stylePrompt || "";
  dom.customSystemPrompt.value = state.draft.customSystemPrompt || "";
  dom.translateBooks.checked = !!state.draft.translateBooks;
  dom.translateSigns.checked = !!state.draft.translateSigns;
  dom.translateTitles.checked = !!state.draft.translateTitles;
  dom.translateFilteredTitles.checked = !!state.draft.translateFilteredTitles;
  dom.translateCustomNames.checked = !!state.draft.translateCustomNames;
  dom.translateItemNames.checked = !!state.draft.translateItemNames;
  dom.translateLore.checked = !!state.draft.translateLore;
  dom.translateCommandOutput.checked = !!state.draft.translateCommandOutput;
  dom.skipCommandLikeText.checked = !!state.draft.skipCommandLikeText;
  dom.resourceEnabled.checked = !!state.draft.resourceEnabled;
  dom.zipPaths.value = state.draft.zipPaths || "";
  dom.sourceLangFiles.value = state.draft.sourceLangFiles || "";
  dom.targetLangFile.value = state.draft.targetLangFile || "ko_kr.json";
  dom.skipIfTargetExists.checked = !!state.draft.skipIfTargetExists;
  dom.batchSize.value = state.draft.batchSize || 40;
  dom.temperature.value = state.draft.temperature || 0.3;
  dom.rpmLimit.value = state.draft.rpmLimit || "";
  dom.tpmLimit.value = state.draft.tpmLimit || "";
  dom.backupSuffix.value = state.draft.backupSuffix || ".bak_translate";
  dom.backup.checked = !!state.draft.backup;
  dom.dryRun.checked = !!state.draft.dryRun;
  dom.checkpointEnabled.checked = !!state.draft.checkpointEnabled;
  dom.continueOnFileError.checked = !!state.draft.continueOnFileError;
  dom.checkpointPath.value = state.draft.checkpointPath || "";
  dom.maxBatchRetries.value = state.draft.maxBatchRetries || 3;
  dom.maxFileWriteRetries.value = state.draft.maxFileWriteRetries || 2;
  dom.skipPatterns.value = state.draft.skipPatterns || "";
  dom.componentPrefixes.value = state.draft.componentPrefixes || "";
  dom.overrides.value = state.draft.overrides || "";
  
  const isCustom = state.draft.provider === "custom_openai" || state.draft.provider === "custom_anthropic";
  dom.customProviderSettings.classList.toggle("hidden", !isCustom);
  if (isCustom) dom.customProviderFormat.value = state.draft.provider;

  renderStaticUi();
  persistDraft();
}

function renderProviderPicker() {
  const providers = state.meta.providers || FALLBACK_META.providers;
  const current = state.draft?.provider || buildDefaultDraft().provider;
  
  const groupedProviders = [];
  let customAdded = false;
  for (const p of providers) {
    if (p.id === 'custom_openai' || p.id === 'custom_anthropic') {
      if (!customAdded) {
        groupedProviders.push({
          id: 'custom',
          label: t('providerCustom') || '기타 / Custom',
          default_base_url: '',
          env_var: 'CUSTOM_*_API_KEY'
        });
        customAdded = true;
      }
    } else {
      groupedProviders.push(p);
    }
  }

  const isCustom = current === 'custom_openai' || current === 'custom_anthropic';

  dom.providerPicker.innerHTML = groupedProviders
    .map((provider) => {
      const activeClass = (provider.id === current || (provider.id === 'custom' && isCustom)) ? "active" : "";
      return `
        <button type="button" class="provider-card ${activeClass}" data-provider-id="${escapeHtml(provider.id)}">
          <strong>${escapeHtml(provider.label)}</strong>
          <span class="provider-url">${escapeHtml(provider.default_base_url)}</span>
          <span class="provider-env">${escapeHtml(provider.env_var)}</span>
        </button>
      `;
    })
    .join("");

  dom.geminiWarning.classList.toggle("hidden", current !== "gemini");
  dom.customProviderSettings.classList.toggle("hidden", !isCustom);

  dom.providerPicker.querySelectorAll("[data-provider-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const providerId = button.dataset.providerId;
      const prev = state.draft?.provider;
      const previousDefault = providerDefaultUrl(prev);
      
      let nextProviderId = providerId;
      if (providerId === 'custom') {
        nextProviderId = dom.customProviderFormat.value || 'custom_openai';
      }
      
      const nextDefault = providerDefaultUrl(nextProviderId);
      state.draft = { ...collectDraft(), provider: nextProviderId };
      if (!dom.baseUrl.value.trim() || dom.baseUrl.value.trim() === previousDefault) {
        dom.baseUrl.value = nextDefault;
      }
      renderProviderPicker();
      updateBaseUrlHelp();
      persistDraft();
    });
  });
}

function renderTargetLanguageOptions() {
  const current = state.draft?.targetLanguagePreset || "ko";
  const options = [
    ["ko", t("targetPreset_ko")],
    ["en", t("targetPreset_en")],
    ["ja", t("targetPreset_ja")],
    ["custom", t("targetPreset_custom")],
  ];
  dom.targetLanguagePreset.innerHTML = options
    .map(([value, label]) => `<option value="${value}">${escapeHtml(label)}</option>`)
    .join("");
  dom.targetLanguagePreset.value = current;
}

function renderStylePresetOptions() {
  const presets = state.meta.style_presets || FALLBACK_META.style_presets;
  const current = state.draft?.stylePreset || "neutral";
  dom.stylePreset.innerHTML = presets
    .map((preset) => `<option value="${preset}">${escapeHtml(t(`stylePreset_${preset}`))}</option>`)
    .join("");
  dom.stylePreset.value = presets.includes(current) ? current : "neutral";
}

function updateStylePresetHelp() {
  dom.stylePresetHelp.textContent = t(`stylePresetDesc_${dom.stylePreset.value}`);
}

function toggleCustomLanguageField() {
  dom.customLanguageField.classList.toggle("hidden", dom.targetLanguagePreset.value !== "custom");
}

function toggleResourcePanel() {
  const disabled = !dom.resourceEnabled.checked;
  dom.resourcePanel.classList.toggle("is-disabled", disabled);
  dom.resourcePanel.classList.toggle("hidden", disabled);
}

function updateBaseUrlHelp() {
  const provider = providerFromPicker();
  const meta = providerMetaById(provider);
  dom.baseUrlHelp.textContent = formatTemplate(t("baseUrlHelp"), {
    url: meta?.default_base_url || "",
    env: meta?.env_var || "",
  });
}

function providerFromPicker() {
  return state.draft?.provider || buildDefaultDraft().provider;
}

function providerMetaById(providerId) {
  return (state.meta.providers || FALLBACK_META.providers).find((item) => item.id === providerId);
}

function providerDefaultUrl(providerId) {
  return providerMetaById(providerId)?.default_base_url || "";
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

function buildPayload(forceDryRun, resumeFromCheckpoint = false) {
  const draft = collectDraft();
  const targetLanguage =
    draft.targetLanguagePreset === "custom"
      ? draft.customLanguage.trim()
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
      provider: draft.provider,
      api_key: draft.apiKey.trim(),
      base_url: draft.baseUrl.trim(),
      model: draft.model.trim(),
      request_timeout: Number(draft.requestTimeout) || 120,
      rpm_limit: Number(draft.rpmLimit) || 0,
      tpm_limit: Number(draft.tpmLimit) || 0,
    },
    prompt: {
      target_language: targetLanguage || "한국어",
      style_preset: draft.stylePreset,
      style_prompt: draft.stylePrompt,
      custom_system_prompt: draft.customSystemPrompt,
    },
    scan: {
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
    runtime: {
      checkpoint_enabled: draft.checkpointEnabled,
      checkpoint_path: draft.checkpointPath.trim(),
      resume_from_checkpoint: resumeFromCheckpoint,
      continue_on_file_error: draft.continueOnFileError,
      max_batch_retries: Number(draft.maxBatchRetries) || 3,
      max_file_write_retries: Number(draft.maxFileWriteRetries) || 2,
    },
  };
}

async function loadModels() {
  dom.modelCatalogStatus.textContent = t("modelCatalogLoading");
  dom.loadModelsButton.disabled = true;
  try {
    const response = await fetch("/api/models", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: buildPayload(true) }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }
    state.modelCatalog = data.models || [];
    dom.modelCatalogStatus.textContent = formatTemplate(t("modelCatalogLoaded"), {
      count: state.modelCatalog.length,
    });
    renderModelCatalog();
  } catch (error) {
    state.modelCatalog = [];
    dom.modelCatalogStatus.textContent = formatTemplate(t("modelCatalogError"), { message: error.message });
    renderModelCatalog();
  } finally {
    dom.loadModelsButton.disabled = false;
  }
}

function renderModelCatalog() {
  const models = state.modelCatalog || [];
  const datalist = document.getElementById("modelSuggestions");
  datalist.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model.id)}"></option>`)
    .join("");

  if (!models.length) {
    dom.modelCatalog.innerHTML = `<div class="model-chip"><strong>${escapeHtml(t("modelCatalogIdle"))}</strong></div>`;
    return;
  }

  dom.modelCatalog.innerHTML = models
    .slice(0, 40)
    .map(
      (model) => `
        <button type="button" class="model-chip" data-model-id="${escapeHtml(model.id)}">
          <strong>${escapeHtml(model.display_name || model.id)}</strong>
          <span>${escapeHtml(model.id)}</span>
          <span>${escapeHtml(model.description || "")}</span>
        </button>
      `
    )
    .join("");

  dom.modelCatalog.querySelectorAll("[data-model-id]").forEach((button) => {
    button.addEventListener("click", () => {
      dom.model.value = button.dataset.modelId;
      persistDraft();
    });
  });
}

async function improveStylePrompt() {
  const brief = dom.styleBrief.value.trim();
  if (!brief) {
    dom.styleAssistStatus.textContent = t("helpStyleBrief");
    return;
  }
  dom.improveStyleButton.disabled = true;
  dom.styleAssistStatus.textContent = t("assistLoading");
  try {
    const response = await fetch("/api/prompt-assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: buildPayload(true), brief }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }
    const current = dom.stylePrompt.value.trim();
    dom.stylePrompt.value = current ? `${current}\n\n${data.enhanced_prompt}` : data.enhanced_prompt;
    dom.styleAssistStatus.textContent = t("assistDone");
    persistDraft();
  } catch (error) {
    dom.styleAssistStatus.textContent = formatTemplate(t("assistError"), { message: error.message });
  } finally {
    dom.improveStyleButton.disabled = false;
  }
}

function applyScopePreset(preset) {
  const apply = (options) => {
    dom.translateBooks.checked = options.translateBooks;
    dom.translateSigns.checked = options.translateSigns;
    dom.translateTitles.checked = options.translateTitles;
    dom.translateFilteredTitles.checked = options.translateFilteredTitles;
    dom.translateCustomNames.checked = options.translateCustomNames;
    dom.translateItemNames.checked = options.translateItemNames;
    dom.translateLore.checked = options.translateLore;
    dom.translateCommandOutput.checked = options.translateCommandOutput;
    dom.skipCommandLikeText.checked = options.skipCommandLikeText;
  };

  if (preset === "story") {
    apply({
      translateBooks: true,
      translateSigns: true,
      translateTitles: true,
      translateFilteredTitles: true,
      translateCustomNames: true,
      translateItemNames: false,
      translateLore: false,
      translateCommandOutput: true,
      skipCommandLikeText: true,
    });
    return;
  }

  if (preset === "all") {
    apply({
      translateBooks: true,
      translateSigns: true,
      translateTitles: true,
      translateFilteredTitles: true,
      translateCustomNames: true,
      translateItemNames: true,
      translateLore: true,
      translateCommandOutput: true,
      skipCommandLikeText: true,
    });
    return;
  }

  apply({
    translateBooks: true,
    translateSigns: true,
    translateTitles: true,
    translateFilteredTitles: true,
    translateCustomNames: true,
    translateItemNames: true,
    translateLore: true,
    translateCommandOutput: true,
    skipCommandLikeText: true,
  });
}

async function submitJob(forceDryRun) {
  return startJob({
    forceDryRun,
    resumeFromCheckpoint: false,
    localEventKey: forceDryRun ? "localScanStarted" : "localTranslateStarted",
  });
}

async function resumeJob() {
  return startJob({
    forceDryRun: false,
    resumeFromCheckpoint: true,
    localEventKey: "localResumeStarted",
  });
}

async function startJob({ forceDryRun, resumeFromCheckpoint, localEventKey }) {
  setRunButtonsDisabled(true);
  try {
    const response = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: buildPayload(forceDryRun, resumeFromCheckpoint) }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }
    state.activeJobId = data.id;
    state.job = data;
    state.localEvents = [];
    pushLocalEvent(localEventKey);
    startPolling();
    renderMonitor();
  } catch (error) {
    pushLocalEvent("localSubmitError", { message: error.message }, true);
    setRunButtonsDisabled(false);
    renderMonitor();
  }
}

async function cancelJob() {
  if (!state.activeJobId) {
    return;
  }

  dom.cancelButton.disabled = true;
  try {
    const response = await fetch(`/api/jobs/${state.activeJobId}/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }
    state.job = data;
    pushLocalEvent("localCancelRequested");
  } catch (error) {
    pushLocalEvent("localCancelError", { message: error.message }, true);
  } finally {
    renderMonitor();
  }
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
    const response = await fetch(`/api/jobs/${state.activeJobId}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Polling failed");
    }
    state.job = data;
    if (["completed", "failed", "cancelled"].includes(data.status)) {
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
  const status = state.job?.status || "idle";
  const running = disabled || status === "queued" || status === "running";
  const hasWorldDir = Boolean(dom.worldDir.value.trim());
  const canResume = !running && hasWorldDir && (state.job ? Boolean(state.job.can_resume) : dom.checkpointEnabled.checked);

  dom.scanButton.disabled = running;
  dom.translateButton.disabled = running;
  dom.resumeButton.disabled = !canResume;
  dom.cancelButton.disabled = !state.activeJobId || !running;
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
  state.modelCatalog = [];
  populateForm(buildDefaultDraft());
  dom.modelCatalogStatus.textContent = "";
  pushLocalEvent("localReset");
  renderMonitor();
}

function pushLocalEvent(key, params = {}, error = false) {
  state.localEvents.unshift({
    timestamp: new Date().toISOString(),
    event: key,
    params,
    error,
    local: true,
  });
  state.localEvents = state.localEvents.slice(0, 20);
}

function renderMonitor() {
  const job = state.job;
  const progress = job?.progress || {
    phase: "idle",
    percent: 0,
    processed_files: 0,
    total_files: 0,
    processed_texts: 0,
    changed_file_count: 0,
    candidate_file_count: 0,
    last_event_at: "",
    current_file: "",
    current_activity: "",
  };
  const status = job?.status || "idle";
  const running = status === "running";
  const resumable = canResumeFromState(job);
  const summary = job?.summary || buildPayload(dom.dryRun?.checked || false);
  const providerId = summary.provider || summary.api?.provider || providerFromPicker();
  const providerLabel = providerMetaById(providerId)?.label || providerId;

  setRunButtonsDisabled(false);
  dom.statusPill.textContent = statusLabel(status);
  dom.livePulse.classList.toggle("active", running);
  dom.progressNumber.textContent = `${Math.round(progress.percent || 0)}%`;
  dom.progressBar.style.width = `${Math.max(0, Math.min(100, progress.percent || 0))}%`;
  dom.monitorSummary.textContent = buildSummary(status, progress, job?.error || "", resumable);
  dom.runHint.textContent = runHintLabel(status, resumable);
  dom.statPhase.textContent = phaseLabel(progress.phase || "idle");
  dom.statFiles.textContent = `${progress.processed_files || 0} / ${progress.total_files || 0}`;
  dom.statTexts.textContent = String(progress.processed_texts || 0);
  dom.statChanged.textContent = String(progress.changed_file_count || job?.result?.changed_file_count || 0);
  dom.statCandidates.textContent = String(progress.candidate_file_count || job?.result?.candidate_file_count || 0);
  dom.statLastUpdate.textContent = formatRelative(progress.last_event_at);
  dom.currentProvider.textContent = providerLabel;
  dom.currentModel.textContent = summary.model || summary.api?.model || dom.model.value || "—";
  dom.currentActivity.textContent = activityLabel(progress.current_activity || progress.phase || "idle");
  dom.currentFile.textContent = progress.current_file || "—";
  dom.resultPanel.textContent = job?.result ? JSON.stringify(job.result, null, 2) : t("emptyResult");

  const timelineEvents = [
    ...(job?.events || []).map((event) => ({ ...event, local: false })),
    ...state.localEvents,
  ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  renderTimeline(timelineEvents.slice(0, 60));

  const candidateCount = progress.candidate_file_count || job?.result?.candidate_file_count || 0;
  if (candidateCount > 0 && status !== 'running' && status !== 'queued') {
      const estimatedTokens = candidateCount * 150;
      const tpm = Number(dom.tpmLimit.value) || 0;
      const rpm = Number(dom.rpmLimit.value) || 0;
      const batchSize = Number(dom.batchSize.value) || 40;
      
      let estSeconds = 0;
      if (tpm > 0) estSeconds = Math.max(estSeconds, (estimatedTokens / tpm) * 60);
      if (rpm > 0) estSeconds = Math.max(estSeconds, ((candidateCount / batchSize) / rpm) * 60);
      
      const timeStr = estSeconds > 0 ? `~ ${Math.ceil(estSeconds / 60)} min` : "(No rate limit)";
      
      dom.estScale.innerHTML = `~${estimatedTokens} tokens (${candidateCount} files)`;
      dom.estTime.innerHTML = timeStr;
  } else {
      dom.estScale.innerHTML = `-`;
      dom.estTime.innerHTML = `-`;
  }
}

function renderTimeline(events) {
  if (!events.length) {
    dom.timeline.innerHTML = `<div class="timeline-item"><p>${escapeHtml(t("emptyTimeline"))}</p></div>`;
    return;
  }

  dom.timeline.innerHTML = events
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
      return formatTemplate(t("eventResourcePackDone"), { count: event.count || 0 });
    case "scan_start":
      return formatTemplate(t("eventScanStart"), { total: event.total_files || 0 });
    case "file_start":
      return formatTemplate(t("eventFileStart"), {
        index: event.index || 0,
        total: event.total || 0,
        file: baseName(event.file),
      });
    case "file_done":
      return formatTemplate(t("eventFileDone"), {
        index: event.index || 0,
        total: event.total || 0,
        file: baseName(event.file),
        changed: event.changed_chunks || 0,
        candidates: event.candidates || 0,
      });
    case "translation_batch_start":
      return formatTemplate(t("eventBatchStart"), { count: event.batch_size || 0 });
    case "translation_batch_done":
      return formatTemplate(t("eventBatchDone"), { count: event.batch_size || 0 });
    case "translation_batch_error":
      return formatTemplate(t("eventBatchError"), { message: event.message || "" });
    case "resource_pack_skipped":
      return formatTemplate(t("eventResourcePackSkipped"), { file: baseName(event.zip_path || event.file || "") });
    case "checkpoint_loaded":
      return formatTemplate(t("eventCheckpointLoaded"), {
        files: event.completed_region_files || 0,
        packs: event.completed_resource_packs || 0,
      });
    case "file_error":
      return formatTemplate(t("eventFileError"), { message: event.message || "" });
    case "file_write_retry":
      return formatTemplate(t("eventWriteRetry"), { message: event.message || "" });
    case "job_cancel_requested":
      return t("eventCancelRequested");
    case "cancelled":
      return t("eventCancelled");
    case "fatal_error":
      return formatTemplate(t("eventFatalError"), { message: event.message || "" });
    case "done":
      return formatTemplate(t("eventDone"), {
        changed: event.changed_file_count || 0,
        candidates: event.candidate_file_count || 0,
      });
    case "job_cancelled":
      return t("eventCancelled");
    case "job_completed":
      return t("eventCompleted");
    case "job_failed":
      return formatTemplate(t("eventFailed"), { message: event.message || "" });
    default:
      return formatTemplate(t("eventUnknown"), { event: event.event });
  }
}

function buildSummary(status, progress, errorMessage, resumable) {
  switch (status) {
    case "queued":
      return t("summaryQueued");
    case "running":
      return t("summaryRunning");
    case "cancelled":
      return t("summaryCancelled");
    case "completed":
      return formatTemplate(t("summaryCompleted"), {
        changed: progress.changed_file_count || 0,
        candidates: progress.candidate_file_count || 0,
      });
    case "failed":
      return errorMessage ? `${t("summaryFailed")} ${errorMessage}`.trim() : t("summaryFailed");
    default:
      return t("summaryIdle");
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
    case "cancelled":
      return t("statusCancelled");
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
    case "translate":
      return t("phaseTranslate");
    case "cancelled":
      return t("phaseCancelled");
    case "done":
      return t("phaseDone");
    case "failed":
      return t("phaseFailed");
    default:
      return t("phaseIdle");
  }
}

function activityLabel(activity) {
  switch (activity) {
    case "preparing":
      return t("activityPreparing");
    case "resource_pack":
    case "resource_pack_start":
      return t("activityResourcePack");
    case "scan_start":
      return t("activityScanStart");
    case "file_start":
      return t("activityFileStart");
    case "file_done":
      return t("activityFileDone");
    case "translation_batch_start":
      return t("activityBatchStart");
    case "translation_batch_done":
      return t("activityBatchDone");
    case "translation_batch_error":
      return t("activityBatchError");
    case "resource_pack_skipped":
      return t("activityResourcePackSkipped");
    case "checkpoint_loaded":
      return t("activityCheckpointLoaded");
    case "file_error":
      return t("activityFileError");
    case "file_write_retry":
      return t("activityFileWriteRetry");
    case "cancel_requested":
    case "job_cancel_requested":
      return t("activityCancelRequested");
    case "cancelled":
      return t("activityCancelled");
    case "done":
      return t("activityDone");
    case "failed":
    case "fatal_error":
      return t("activityFailed");
    default:
      return phaseLabel(activity);
  }
}

function canResumeFromState(job) {
  if (job) {
    return Boolean(job.can_resume);
  }
  return Boolean(dom.worldDir.value.trim()) && dom.checkpointEnabled.checked;
}

function runHintLabel(status, resumable) {
  switch (status) {
    case "running":
    case "queued":
      return t("runHintRunning");
    case "cancelled":
      return t("runHintCancelled");
    case "failed":
      return resumable ? t("runHintFailed") : t("runHintReady");
    case "completed":
      return resumable ? t("runHintResume") : t("runHintReady");
    case "idle":
    default:
      return resumable ? t("runHintResume") : dom.worldDir.value.trim() ? t("runHintReady") : t("runHintIdle");
  }
}

function formatRelative(iso) {
  if (!iso) {
    return "—";
  }
  const diffSeconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  if (diffSeconds < 5) {
    return t("relativeNow");
  }
  if (diffSeconds < 60) {
    return formatTemplate(t("relativeSeconds"), { count: diffSeconds });
  }
  return formatTemplate(t("relativeMinutes"), { count: Math.floor(diffSeconds / 60) });
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

function t(key) {
  return I18N[state.lang]?.[key] ?? I18N.ko[key] ?? key;
}

function formatTemplate(template, values) {
  return String(template).replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ""));
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
