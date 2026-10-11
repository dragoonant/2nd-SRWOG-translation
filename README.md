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

- **Your own copy of the game**, unpacked into a folder (not an ISO file; see below). This
  repo contains no game data: the installer builds the patch from your copy.
- **RPCS3**, with the PS3 firmware installed and the game booting in Japanese.
- **Windows 10 or 11.**
- **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/). In the
  Python installer, tick **Add python.exe to PATH**.
- About **13 GB** of free disk space for the installer's work folder.

Real PS3 hardware is not supported.

## Installing

1. **Download the patch.** On this page click **Code → Download ZIP**, and unzip it anywhere.
2. **Make sure the game is unpacked.** RPCS3 should list it from a folder like
   `RPCS3\dev_hdd0\disc\BLJS10133\`, with `PS3_GAME` inside. If you only have an ISO,
   open it with [7-Zip](https://www.7-zip.org/) and extract everything into that folder,
   then boot the game once in RPCS3.
3. **Double-click `Install.bat`.** It finds RPCS3 and the game by itself (or asks you where
   they are), and offers to install the two Python packages it needs. The first run takes
   about 20 minutes. When it says **Done**, start the game in RPCS3: it is in English.

If the game asks to install data on its first boot, confirm with **Cross**. In the game's
own menus, **Circle** confirms.

What the installer does, step by step:

1. Checks that your game files are the original Japanese release and makes a backup copy
   in a work folder (`srw2og-work` in your user folder).
2. Decrypts the game's EBOOT using your own RPCS3 and firmware.
3. Unpacks the game archives and builds the English files.
4. Copies them into your game, with the file dates the game checks on every boot.

Your game is changed only in the last step, and the backup lets you undo it.

### Updating

Download the new version, unzip it, and double-click `Install.bat` again. It reuses the
work folder, so updates take about 15 minutes.

### Uninstalling

Double-click `Uninstall.bat`. It puts every original file back from the backup. You can
then delete the `srw2og-work` folder.

### Options

Run the installer from a command prompt to pass options:

```bash
python install.py --rpcs3 "D:\Emulators\RPCS3" --game "D:\Games\BLJS10133" --work "D:\srw2og-work"
```

- `--rpcs3`: the folder that holds `rpcs3.exe`.
- `--game`: the folder that holds `PS3_GAME`.
- `--work`: where the backup and build files go.
- `--uninstall`: restore the original files.

### Troubleshooting

- **"is not the original file from the Japanese release"**: another patch was applied
  to the game, or the dump differs. Restore the original files (or dump the disc again)
  and run the installer again.
- **"RPCS3 could not decrypt the EBOOT"**: install the PS3 firmware in RPCS3
  (**File → Install Firmware**) and check the game boots.
- **The game says its data is corrupted (「ゲームデータが壊れています」)**: the game
  compares the size and date of its archives with its installed copy on every boot. Run
  `Install.bat` again. If that does not help, run
  `python tools\deploy.py install "%USERPROFILE%\srw2og-work\build" --reinstall`, boot the
  game and let it reinstall its data (about 10 minutes).

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
  English and each string's budget. Edit the `en` fields, then rebuild and install with
  `python install.py`, or build without installing with
  `python tools\build.py --work "%USERPROFILE%\srw2og-work" --out build`.
- `tools/` holds the Python tools. Each script explains its usage at the top.
  `tools/fitcheck.py` checks widths and glossary use.
- `glossary/` holds the names, `textures/` the picture-text specs, `docs/` the file formats.
- `choices.md` and `deviations.md` list the wording decisions still open.

## Credits

- Translation project: evilgouki, with tools and the first-pass translation by
  Claude (Anthropic).
- Naming follows the *OG: Original Generations* PS2 fan translation, and is checked against
  the Akurasu SRW wiki.
- *Super Robot Wars* belongs to Bandai Namco Entertainment. This is an unofficial fan
  project. Please buy the game.

## Licence

The installer, tools and documentation are under the [MIT licence](LICENSE). The game and
its contents are not ours and are not included.
