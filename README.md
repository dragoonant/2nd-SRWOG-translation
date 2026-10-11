# 2nd Super Robot Wars OG — English Translation (PS3, BLJS10133)

An English translation patch for *Dai-2-Ji Super Robot Taisen OG* (PlayStation 3, Japan,
BLJS10133), played in the [RPCS3](https://rpcs3.net) emulator.

The names and terms follow the *Super Robot Wars OG: Original Generations* PS2 fan patch,
so they match what players already know from the earlier games. The game's text renderer is
patched to use a proportional font, so English reads like English and not like spaced-out
Japanese.

> **Status: playable beta.** All 84,516 translatable strings have English. A first pass was
> machine-translated from the Japanese, then checked against the glossary and the on-screen
> width limits, and now a human is editing it line by line. Expect awkward lines, a few
> overlaps, and some Japanese left on screen. Bug reports are welcome (see
> [Reporting problems](#reporting-problems)).

## What you need

- **Your own copy of the game.** This repo contains no game data. You build the patch from
  your own dump of the Japanese disc (BLJS10133).
- **RPCS3**, with PS3 firmware installed, and the game booting in Japanese.
- **Windows 10 or 11.** The build uses two Windows fonts (Bahnschrift and Arial Bold) to
  draw the English text inside pictures.
- **Python 3.10 or newer**, with two packages:
  ```bash
  pip install pycryptodome pillow
  ```
- About 25 GB of free disk space for the working files.

Real PS3 hardware is not supported.

## Installing

### 1. Download the patch

Click **Code → Download ZIP** on this page and unzip it, or clone it:

```bash
git clone https://github.com/dragoonant/2nd-SRWOG-translation.git
```

The commands below assume you are in that folder, in PowerShell.

### 2. Put the game where RPCS3 can see it

The installer expects the game as an extracted disc folder inside RPCS3:

```
<RPCS3>\dev_hdd0\disc\BLJS10133\PS3_GAME\USRDIR\EBOOT.BIN
<RPCS3>\dev_hdd0\disc\BLJS10133\PS3_GAME\USRDIR\PSARC\*.psarc.sdat
```

If you have an ISO, open it (or mount it) and copy its contents into
`<RPCS3>\dev_hdd0\disc\BLJS10133\`. Boot the game once in RPCS3 and let it finish its
first-time data install, so you know your copy works.

### 3. Decrypt the EBOOT

In RPCS3, choose **Utilities → Decrypt PS3 Binaries** and pick
`PS3_GAME\USRDIR\EBOOT.BIN`. RPCS3 writes `EBOOT.elf` next to it. This needs the
firmware keys from your own RPCS3 install, so the patch cannot do it for you.

### 4. Set up a working folder

The build reads the original files from a working folder and never changes your game until
step 6. Set two variables (change the paths to suit your PC):

```powershell
$RPCS3 = "C:\RPCS3"
$WORK  = "C:\srw2og-work"
```

Then copy the originals in and unpack them. This takes a few minutes:

```powershell
$USR = "$RPCS3\dev_hdd0\disc\BLJS10133\PS3_GAME\USRDIR"
New-Item -ItemType Directory -Force "$WORK\pristine\USRDIR\PSARC", "$WORK\dec", "$WORK\ext" | Out-Null
Copy-Item "$USR\EBOOT.BIN", "$USR\EBOOT.elf" "$WORK\pristine\USRDIR\"
foreach ($a in "Logic","Common","General2d","General3d","Battle") {
  Copy-Item "$USR\PSARC\$a.psarc.sdat" "$WORK\pristine\USRDIR\PSARC\"
  python tools\sdat.py decrypt "$WORK\pristine\USRDIR\PSARC\$a.psarc.sdat" "$WORK\dec\$a.psarc"
  python tools\psarc.py extract "$WORK\dec\$a.psarc" "$WORK\ext\$a"
}
```

`pristine` now holds untouched copies of your game files. Keep it: the uninstall step
restores from it.

### 5. Build the patch

```powershell
python tools\build.py --work $WORK --out build
```

When it finishes it prints `done: N archive(s), 0 problem(s)`. The patched files are in
`build\USRDIR\`.

### 6. Install it into RPCS3

```powershell
python tools\deploy.py install build --rpcs3 $RPCS3 --pristine "$WORK\pristine\USRDIR"
```

This copies the patched `EBOOT.BIN` and archives into your disc folder and into the game's
installed data folder, with the timestamps the game checks. Boot the game in RPCS3 and it
starts in English.

If you never let the game do its first-time install (step 2), it does it now from the
patched files. Confirm the install prompt with **Cross**. In the game's own menus,
**Circle** confirms.

### Updating

Download the new version (or `git pull`), then repeat steps 5 and 6. The working folder
from step 4 is reused.

### Uninstalling

```powershell
python tools\deploy.py rollback --rpcs3 $RPCS3 --pristine "$WORK\pristine\USRDIR"
```

This puts every original file back. `deploy.py status` shows which files are patched.

### If the game says its data is corrupted

The game checks the size and date of its archives on every boot and shows
「ゲームデータが壊れています」 if the disc copy and the installed copy disagree. The installer
keeps them in step. If you copied files by hand, run step 6 again. If that does not help,
reinstall the game data from scratch:

```powershell
python tools\deploy.py install build --rpcs3 $RPCS3 --pristine "$WORK\pristine\USRDIR" --reinstall
```

Then boot the game and let it reinstall (about 10 minutes).

## Design choices

### An independent translation

This is a new translation from the Japanese, with its own tools. It does not reuse text or
code from the other 2nd OG English projects. Every file format was worked out from the game
itself and is documented in [`docs/`](docs/).

### Names and terms: the OGs fan patch first

The English names come from the *OG: Original Generations* PS2 fan patch, the game that
comes right before 2nd OG, so the names are the ones players already know. They are checked
against the [Akurasu](https://akurasu.net/wiki/) wiki. Names the OGs patch never uses come
from Akurasu. Where the two disagree, the OGs form wins for now, and every disagreement is
listed in [`deviations.md`](deviations.md) for a final decision.

What that means in practice:

- **Short vowels and umlauts**, as in OGs: Kyosuke, Ryusei, Shu, Lüne, Sänger, Rätsel,
  Wildwürger (not Kyousuke, Ryuusei, Shuu, Ryuune, Sanger).
  The game's font had no **ü**, so we drew one.
- **"Custom" and "Type"** instead of romanized Kai and Shiki: Hiryu Custom,
  Grungust Type 3.
- **OGs Spirit Command names**: Valor, Wall, Bullseye, Pierce, Gain, Spirit, Hope
  (not Hotblood, Iron Wall, Sure-Hit, Direct Hit).
- **Altalion** for アルテリオン, everywhere.

The glossary lives in [`glossary/`](glossary/). `tools/fitcheck.py` checks every line against it
and flags any non-standard spelling of a known name.

### Dialogue style

Taken from the OGs patch, so the two games read the same:

- **No honorifics** (no -san, -kun, -chan). The one exception is "Rishu-sensei".
- **Ranks written in full**: Captain, Lieutenant, Commander. Never "Lt."
- **No quote marks** on spoken lines (the name box shows who is talking).
  Inner thoughts go in (parentheses).
- Natural, contraction-heavy English that keeps each character's voice: Masaki brash,
  Shu cool and formal, Ryusei excitable, Kyosuke terse, Excellen playful.

The full rules are in [`docs/style-guide.md`](docs/style-guide.md).

### A proportional font

The game lays out every character in a fixed 32-pixel box, which turns English into
widely spaced letters and leaves little room per line. The patch changes six text routines
in the EBOOT so each letter advances by its own width, and generates proportional Latin
letters from the game's own font (with real descenders on g, j, p, q, y). Japanese text that
is still untranslated keeps its normal spacing. Details:
[`docs/eboot-renderer.md`](docs/eboot-renderer.md), [`docs/rendering.md`](docs/rendering.md).

### Fitting English into Japanese-sized boxes

The game never wraps text by itself, so every line is measured in pixels before it goes in:
832 pixels per line for story dialogue, 704 for battle quotes, and each menu label
against its own window. Lines that do not fit are re-translated shorter. Where a box is very
tight, a short word is used ("Live" for 実戦, "Off" for 非表示, "EXP Earned").

### Text inside pictures

Some on-screen words are pictures, not text: the map overlays, battle badges, the
intermission title and the stage title cards. These are repainted in English, each kept
inside its original pixel box, which forces abbreviations: **SUP ATK / SUP DEF** (support
attack and defence), **ATK / CTR** (attack / counter), **RE-ATK**, **CMB** (combine).
Stage title cards read "Scenario N".

### What stays Japanese on purpose

- Internal keys the engine matches byte for byte (speaker keys, event labels, file paths).
  Translating them would break the game.
- A few short words in the stage scripts that look like script labels.
- The legal notice screen and some logos, which are pictures. These may be done before the
  final release.

### How it was translated

The first pass was machine translation with Claude (Anthropic), done one scene at a time
with the speaker names, the previous scene, the glossary, the style guide and each line's
pixel budget. Every result was checked automatically: control codes kept, line widths
respected, glossary names used. Anything that failed was retried or left in Japanese and
logged. That draft is now being edited by hand, line by line, which is the main difference
we aim for at release.

## Known issues

- The edit pass is in progress, so some lines read stiffly or are slightly off.
- A few windows may still overlap or cut off text. Please report them.
- Background art in event scenes looks soft. That is the original artwork, not the patch.
- Untested so far: every route to the end, both endings, and all library pages.

## Reporting problems

Open an [issue](https://github.com/dragoonant/2nd-SRWOG-translation/issues) with a
screenshot (F12 in RPCS3) and roughly where you were: the scenario number and what was
happening. For text problems, quote the line.

## For contributors

- `worksheets/` holds the translation: one JSON file per game file, with the Japanese, the
  English and each string's budget. Edit the `en` fields, then rebuild.
- `tools/` holds the Python tools. Each script explains its usage at the top.
  `tools/fitcheck.py` checks widths and glossary use.
- `glossary/` holds the names, `textures/` the picture-text specs, `docs/` the file formats.
- `choices.md` and `deviations.md` list the wording decisions still open.

## Credits

- Translation project: evilgouki (dragoonant), with tools and the first-pass translation by
  Claude (Anthropic).
- Naming follows the *OG: Original Generations* PS2 fan translation, and is checked against
  the Akurasu SRW wiki.
- *Super Robot Wars* belongs to Bandai Namco Entertainment. This is an unofficial fan
  project. Please buy the game.
