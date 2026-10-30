[CmdletBinding()]
param([string]$Destination = (Join-Path $PSScriptRoot '..\repos'))

$ErrorActionPreference = 'Continue'
$env:GIT_LFS_SKIP_SMUDGE = '1'

$repositories = @(
    @{ Repo = 'abdibrokhim/humanaize'; Branch = 'main'; DirName = 'HumanAI-main' },
    @{ Repo = 'blader/humanizer'; Branch = 'main'; DirName = 'Humanizer-main' },
    @{ Repo = 'egorsmkv/NLLB-Translator'; Branch = ''; DirName = 'NLLB_translator' },
    @{ Repo = 'fighting41love/funNLP'; Branch = 'main'; DirName = 'NLP-main' },
    @{ Repo = 'MozillaSecurity/dharma'; Branch = 'master'; DirName = 'dharma-master' },
    @{ Repo = 'fidelisrafael/esperanto-analyzer'; Branch = 'master'; DirName = 'esperanto-analyzer-master' },
    @{ Repo = 'kanyun-inc/fairseq-gec'; Branch = 'master'; DirName = 'fairseq-gec-master' },
    @{ Repo = 'aiko-tanaka/Grammar-Dictionaries'; Branch = 'main'; DirName = 'Grammar-Dictionaries-main' },
    @{ Repo = 'zysyyz/Smali-grammar-and-learning'; Branch = 'main'; DirName = 'grammar-learning-main' },
    @{ Repo = 'antlr/grammars-v4'; Branch = 'master'; DirName = 'grammars-v4-master' },
    @{ Repo = 'Automattic/harper'; Branch = 'master'; DirName = 'harper-master' },
    @{ Repo = 'google/langextract'; Branch = 'main'; DirName = 'langextract-main' },
    @{ Repo = 'jxmorris12/language_tool_python'; Branch = 'master'; DirName = 'language_tool_python-master' },
    @{ Repo = 'cclank/lanshu-awesome-ai-video-kit'; Branch = 'main'; DirName = 'lanshu-awesome-ai-video-kit-main' },
    @{ Repo = 'reader-dict/monolingual'; Branch = 'main'; DirName = 'monolingual-main' },
    @{ Repo = 'google-research/multilingual-t5'; Branch = 'master'; DirName = 'multilingual-master' },
    @{ Repo = 'musescore/MuseScore'; Branch = 'main'; DirName = 'MUSE-main' },
    @{ Repo = 'ohmyzsh/ohmyzsh'; Branch = 'main'; DirName = 'ohm-main' },
    @{ Repo = 'Findus23/pyLanguagetool'; Branch = 'master'; DirName = 'pyLanguagetool-master' },
    @{ Repo = 'fititnt/DicSin-dicionario-sinonimos-portugues-brasileiro'; Branch = 'master'; DirName = 'sinonimos-master' },
    @{ Repo = 'AgentOps-AI/Spellcaster'; Branch = 'master'; DirName = 'Spellcaster-master' },
    @{ Repo = 'xfenix/spellcheck-microservice'; Branch = 'main'; DirName = 'spellcheck-microservice-main' },
    @{ Repo = 'shikijs/textmate-grammars-themes'; Branch = 'main'; DirName = 'textmate-grammars-themes-main' },
    @{ Repo = 'Kyomotoi/AnimeThesaurus'; Branch = 'master'; DirName = 'thesaurus-master' },
    @{ Repo = 'tatuylonen/wikitextprocessor'; Branch = 'main'; DirName = 'wikitextprocessor-main' },
)

$resolvedDestination = [System.IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Force -Path $resolvedDestination | Out-Null

$results = foreach ($item in $repositories) {
    $target = Join-Path $resolvedDestination $item.DirName
    if (Test-Path -LiteralPath $target) { [pscustomobject]@{Repo=$item.Repo;Status="present";Path=$target}; continue }
    if ($item.Branch) {
        & git clone --depth 1 --branch $item.Branch --single-branch "https://github.com/$($item.Repo).git" $target
    } else {
        & git clone --depth 1 "https://github.com/$($item.Repo).git" $target
    }
    [pscustomobject]@{Repo=$item.Repo;Status=(if($LASTEXITCODE -eq 0){"cloned"}else{"failed"});Path=$target}
}
$results | Format-Table -AutoSize
if ($results.Status -contains "failed") { Write-Warning "Algunos repos fallaron - revisa manualmente." }
