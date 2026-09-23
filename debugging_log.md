# Task description

This is the source of a Jekyll based static website visible at https://bmeaut.github.io/snippets/index.html.
The subpages are located in the "snippets" directory, all of them identified by a unique ID in the beginning of the directory name.
Some of them have syntax errors and so they are not visible in the compiled html output.

## Task 1: check for errors 

Your task is to
- fetch the generated html website from the above URL, and
- go along all the subdirectories (snippets) of the "snippets" directory and check whether they are visible in the html output
- also open all the snippets from the web and check whether all the referenced images are visible and there are no formatting issues like unrecognized markup remaining somehow in the html output.
- Create a log of the findings in the "Check log" subsection of this file. Enumerate all snippets in a table here are describe their status as "OK", "invisible", or "visible but misformatted".

### Clarifications

- Check all subdirectories under `snippets/`.
- A snippet is considered visible when it appears on the starting page.
- If it appears on the starting page as a link but its content is rendered incorrectly, classify it as "visible but misformatted".
- For this pass, complete only Task 1 and wait for approval before fixing any errors in Task 2.

## Task 2: fix the errors

Here your task is to go along the "check log" and fix the issues.

# Check log

Audit performed: 2026-09-23

The published starting page was checked against all 112 directories under `snippets/`. Each published snippet page returned HTTP 200. Every referenced image was checked over HTTP; all image URLs returned HTTP 200. The page body text was also checked for unrecognized Jekyll/Liquid markers.

| Snippet directory | Status | Finding |
|---|---|---|
| `0000_MiASnippet` | OK | Page and images render correctly. |
| `0001_SnippetSablon` | OK | Page and images render correctly. |
| `0002_Zarovizsga` | OK | Page and images render correctly. |
| `0101_BevXampp` | OK | Page and images render correctly. |
| `0102_EviplabsGit` | OK | Page and images render correctly. |
| `0103_GitPeldafejlesztes` | OK | Page and images render correctly. |
| `0104_QtSignalsAndSlots` | OK | Page and images render correctly. |
| `0105_Doxygen` | OK | Page and images render correctly. |
| `0114_VerziokezelokOsszehasonlitasa` | OK | Page and images render correctly. |
| `0115_GitPullRequest` | OK | Page and images render correctly. |
| `0116_GitAuth` | OK | Page and images render correctly. |
| `0119_QTest` | OK | Page and images render correctly. |
| `0120_Hibakezeles` | OK | Page and images render correctly. |
| `0121_Cpp11Ptr` | OK | Page and images render correctly. |
| `0126_GitBev` | OK | Page and images render correctly. |
| `0127_DebugRelease` | OK | Page and images render correctly. |
| `0128_GitHalado` | OK | Page and images render correctly. |
| `0129_GitTuzvedelem` | OK | Page and images render correctly. |
| `0130_StdThread` | OK | Page and images render correctly. |
| `0131_QtToolchainHelloWorld` | OK | Page and images render correctly. |
| `0132_QtSocketDemo` | OK | Page and images render correctly. |
| `0133_QtQmlDemo` | OK | Page and images render correctly. |
| `0134_QDataStream` | OK | Page and images render correctly. |
| `0135_QtQmlControlKupac` | OK | Page and images render correctly. |
| `0136_QtQmlCpp` | OK | Page and images render correctly. |
| `0137_GithubForkPullReq` | OK | Page and images render correctly. |
| `0138_GitParancssor` | OK | Page and images render correctly. |
| `0139_GitGyakorlat` | OK | Page and images render correctly. |
| `0200_DesignPatternsBev` | OK | Page and images render correctly. |
| `0201_DpFactory` | OK | Page and images render correctly. |
| `0202_DpAbstactFactory` | OK | Page and images render correctly. |
| `0203_DpBuilder` | OK | Page and images render correctly. |
| `0204_DpLazyInit` | OK | Page and images render correctly. |
| `0205_DpSingleton` | OK | Page and images render correctly. |
| `0206_DpPrototype` | OK | Page and images render correctly. |
| `0207_DpRAII` | OK | Page and images render correctly. |
| `0208_DpComposite` | OK | Page and images render correctly. |
| `0209_DpDecorator` | OK | Page and images render correctly. |
| `0210_DpFacade` | OK | Page and images render correctly. |
| `0211_DpProxy` | OK | Page and images render correctly. |
| `0212_DpObserver` | OK | Page and images render correctly. |
| `0213_DpStrategy` | OK | Page and images render correctly. |
| `0214_DpState` | OK | Page and images render correctly. |
| `0215_DpEgyebek` | invisible | No link to this directory was found on the starting page. |
| `0216_VisitorObserverPelda` | OK | Page and images render correctly. |
| `0217_DpVisitor` | OK | Page and images render correctly. |
| `0218_GlcdTervezesiPelda` | OK | Page and images render correctly. |
| `0219_QtQmlFocus` | OK | Page and images render correctly. |
| `0220_TurkmiteRefactorEsTeszt` | OK | Page and images render correctly. |
| `0221_LiskovModemPelda` | OK | Page and images render correctly. |
| `0221_QtQmlJavascriptImage` | OK | Page and images render correctly. |
| `0222_SOLID` | OK | Page and images render correctly. |
| `0301_JenkinsConfig` | OK | Page and images render correctly. |
| `0302_JenkinsAdvanced` | OK | Page and images render correctly. |
| `0401_PointCloudLib` | OK | Page and images render correctly. |
| `0402_ImageAffineTransform` | OK | Page and images render correctly. |
| `0403_FilterThreshold` | OK | Page and images render correctly. |
| `0404_SuperPixels` | OK | Page and images render correctly. |
| `0405_ActiveContour` | OK | Page and images render correctly. |
| `0500_RJMCMC` | OK | Page and images render correctly. |
| `0600_Vrep` | OK | Page and images render correctly. |
| `0700_LinuxBev` | OK | Page and images render correctly. |
| `0701_LinuxPermissions` | OK | Page and images render correctly. |
| `0702_LinuxPipeline` | OK | Page and images render correctly. |
| `0703_BashBev` | OK | Page and images render correctly. |
| `0704_TerminalShortcuts` | OK | Page and images render correctly. |
| `0705_LinuxFS` | OK | Page and images render correctly. |
| `0706_DockerBev` | OK | Page and images render correctly. |
| `0707_WindowsVM_Alkfejl` | OK | Page and images render correctly. |
| `0800_Luis` | OK | Page and images render correctly. |
| `0900_RandomSzam` | OK | Page and images render correctly. |
| `0901_StopwatchVsDateTime` | OK | Page and images render correctly. |
| `0902_SyncVsAsync` | OK | Page and images render correctly. |
| `0903_DataTemplateSelector` | OK | Page and images render correctly. |
| `1000_MIEsettanulmanySablon` | OK | Page and images render correctly. |
| `1001_MastermindTdd` | OK | Page and images render correctly. |
| `1002_Flashcards` | OK | Page and images render correctly. |
| `1003_FootballResultsWebApp` | OK | Page and images render correctly. |
| `1004_Wordle` | OK | Page and images render correctly. |
| `1005_RAGCourseMaterial` | OK | Page and images render correctly. |
| `1007_KontenerizacioROS` | OK | Page and images render correctly. |
| `1008_NotionPersonalHub` | visible but misformatted | Literal `%}` remains visible in the rendered page text. |
| `1010_AutomatAd` | OK | Page and images render correctly. |
| `1011_cashregisterTdd` | OK | Page and images render correctly. |
| `1012_n8n_basics` | OK | Page and images render correctly. |
| `1013_PyBomberman` | OK | Page and images render correctly. |
| `1014_DroneControl` | OK | Page and images render correctly. |
| `1015_Tessera` | OK | Page and images render correctly. |
| `1016_agent_hierarchy` | OK | Page and images render correctly. |
| `1017_Arcade_VibeCoding` | OK | Page and images render correctly. |
| `1018_LabPontozas` | OK | Page and images render correctly. |
| `1019_SignalGeneration` | OK | Page and images render correctly. |
| `1021_AImless` | OK | Page and images render correctly. |
| `1022_Figma2AndroidUI` | OK | Page and images render correctly. |
| `1023_AIAssistedPIDTuning` | OK | Page and images render correctly. |
| `1025_BiPlatform` | visible but misformatted | Literal `}}` remains visible in the rendered page text. |
| `1026_AIforGeneratingRobotModels` | OK | Page and images render correctly. |
| `1027_AIGrader` | OK | Page and images render correctly. |
| `1028_RalphLoop` | OK | Page and images render correctly. |
| `1030_RustCInterop` | OK | Page and images render correctly. |
| `1031_MobileDesign` | OK | Page and images render correctly. |
| `1032_TeamsIntegration` | invisible | No link to this directory was found on the starting page. |
| `1037_LocalGradingAgent` | OK | Page and images render correctly. |
| `1038_MultiNeedleHaystack` | OK | Page and images render correctly. |
| `1039_ChartReading` | OK | Page and images render correctly. |
| `1040_MCPServerforCalendars` | OK | Page and images render correctly. |
| `1041_ResearchAssisstant` | OK | Page and images render correctly. |
| `1042_SnippetManager` | OK | Page and images render correctly. |
| `1043_AgentSkills` | OK | Page and images render correctly. |
| `1051_AIforRobotWorldGeneration` | OK | Page and images render correctly. |
| `1052_RustCmidlayer` | OK | Page and images render correctly. |
| `AlkFejlHfTanulsagok` | OK | Page and images render correctly. |

Summary: 108 OK, 2 invisible, and 2 visible but misformatted.

