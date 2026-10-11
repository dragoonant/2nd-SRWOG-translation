#!/usr/bin/env python3
"""One-step installer for the 2nd Super Robot Wars OG English patch (RPCS3).

Double-click Install.bat, or run:
  python install.py [--rpcs3 DIR] [--game DIR] [--work DIR] [--yes]
  python install.py --uninstall [--rpcs3 DIR] [--game DIR] [--work DIR]

What it does, in order (each step is skipped when it is already done):
  1. checks Python packages (pycryptodome, pillow) and offers to install them
  2. finds RPCS3 and the game (RPCS3's games.yml, else asks)
  3. checks the game files are the original Japanese release and backs them
     up to WORK/pristine (the uninstaller restores from there)
  4. decrypts the EBOOT with RPCS3 itself (rpcs3.exe --decrypt)
  5. decrypts the five game archives into WORK/dec
  6. builds the English files (tools/build.py) into WORK/build
  7. copies them into the game (tools/deploy.py)

--game is the folder that holds PS3_GAME. --work defaults to a folder named
srw2og-work in your user folder; it needs about 13 GB the first time.
Options for testing: --build-only (stop before step 7), --no-verify (skip
the original-file check in step 3).
"""
import glob
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "tools")
SERIAL = "BLJS10133"
ARCHIVES = ["Logic", "Common", "General2d", "General3d", "Battle"]

# Size and SHA-1 of the original BLJS10133 files, relative to PS3_GAME/USRDIR.
ORIGINAL = {
    "EBOOT.BIN": (14147488, "d4f3386ab9f38f129005794a741c044d8ec3fa08"),
    "PSARC/Battle.psarc.sdat": (1616454320, "70fb4fd78950f674b244f3053d38f2153fbbfecd"),
    "PSARC/Common.psarc.sdat": (292498512, "1bb0d335cdbc14d3fb37145ba61d3270f24746b0"),
    "PSARC/General2d.psarc.sdat": (654157632, "d256fa2769ea6e62148096c29e02271aed2131f3"),
    "PSARC/General3d.psarc.sdat": (1069546080, "d9788e6f0dc4b2ecf1234565c0b061b1834dc258"),
    "PSARC/Logic.psarc.sdat": (26494784, "addbbf7808041115fd6b8cd70d705db2a3e41b4c"),
}
EBOOT_ELF = (14145056, "c997aa412ea02ef699ac7d500bfaf3321b4010c8")
DECRYPTED_SIZE = {"Battle": 1613303039, "Common": 291928064, "General2d": 652882180,
                  "General3d": 1067460900, "Logic": 26442860}
FIRST_RUN_BYTES = 13 * 10**9

YES = False


class Stop(Exception):
    """A problem the user has to fix; the message says how."""


def say(msg=""):
    print(msg, flush=True)


def step(msg):
    say()
    say("== " + msg)


def ask(question, default=True):
    if YES:
        return True
    hint = " [Y/n] " if default else " [y/N] "
    a = input(question + hint).strip().lower()
    return default if not a else a.startswith("y")


def ask_path(question):
    if YES:
        raise Stop(question + " (run again with the folder on the command line)")
    a = input(question + "\n> ").strip().strip('"')
    if not a:
        raise Stop("No folder given.")
    return a


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def matches(path, size_sha):
    size, digest = size_sha
    return os.path.isfile(path) and os.path.getsize(path) == size and sha1(path) == digest


def run_tool(args):
    """Run a repo tool, streaming its output; stop on failure."""
    r = subprocess.run([sys.executable, "-I"] + args)
    if r.returncode != 0:
        raise Stop("%s failed (exit code %d). The messages above say why." % (os.path.basename(args[0]), r.returncode))


# --- 1. Python packages -------------------------------------------------------

def check_packages():
    step("Checking Python packages")
    missing = []
    for module, package in (("Crypto", "pycryptodome"), ("PIL", "pillow")):
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if not missing:
        say("pycryptodome and pillow are installed.")
        return
    say("Missing: " + ", ".join(missing))
    if not ask("Install them now with pip?"):
        raise Stop("Install them with:  %s -m pip install %s" % (sys.executable, " ".join(missing)))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user"] + missing)
    if r.returncode != 0:
        raise Stop("pip could not install %s." % ", ".join(missing))


# --- 2. Find RPCS3 and the game ----------------------------------------------

def rpcs3_exe(folder):
    exe = os.path.join(folder, "rpcs3.exe")
    return exe if os.path.isfile(exe) else None


def find_rpcs3(given):
    step("Finding RPCS3")
    if given:
        if given.lower().endswith(".exe"):
            given = os.path.dirname(given)
        if not rpcs3_exe(given):
            raise Stop("No rpcs3.exe in %s" % given)
        return os.path.abspath(given)
    home = os.path.expanduser("~")
    candidates = [os.path.join(home, "RPCS3"), r"C:\RPCS3", r"C:\Program Files\RPCS3",
                  os.path.join(home, "Desktop", "RPCS3"), os.path.join(home, "Documents", "RPCS3")]
    for pattern in ("Downloads/rpcs3*", "Desktop/rpcs3*", "rpcs3*"):
        candidates += sorted(glob.glob(os.path.join(home, pattern)))
    for c in candidates:
        if rpcs3_exe(c):
            say("Found RPCS3 in %s" % c)
            return c
    while True:
        folder = ask_path("Where is RPCS3? Paste the folder that contains rpcs3.exe:")
        if folder.lower().endswith(".exe"):
            folder = os.path.dirname(folder)
        if rpcs3_exe(folder):
            return os.path.abspath(folder)
        say("No rpcs3.exe there. Try again.")


def games_yml_path(rpcs3):
    """The game's folder as RPCS3's game list records it, or None."""
    for yml in (os.path.join(rpcs3, "config", "games.yml"), os.path.join(rpcs3, "games.yml")):
        if not os.path.isfile(yml):
            continue
        for line in open(yml, encoding="utf-8", errors="replace"):
            if line.startswith(SERIAL + ":"):
                p = line.split(":", 1)[1].strip().strip('"').strip("'")
                return p.replace("$(EmulatorDir)", rpcs3 + "/")
    return None


def usrdir_of(game):
    return os.path.join(game, "PS3_GAME", "USRDIR")


def is_game_folder(game):
    u = usrdir_of(game)
    return os.path.isfile(os.path.join(u, "EBOOT.BIN")) and os.path.isdir(os.path.join(u, "PSARC"))


def find_game(rpcs3, given):
    step("Finding the game (%s)" % SERIAL)
    if given:
        if not is_game_folder(given):
            raise Stop("%s does not look like the game folder: it needs PS3_GAME\\USRDIR\\EBOOT.BIN "
                       "and PS3_GAME\\USRDIR\\PSARC." % given)
        return os.path.abspath(given)
    for g in (games_yml_path(rpcs3), os.path.join(rpcs3, "dev_hdd0", "disc", SERIAL)):
        if not g:
            continue
        if g.lower().endswith(".iso"):
            raise Stop("RPCS3 runs the game from an ISO file (%s). The patch needs the files unpacked: "
                       "open the ISO with 7-Zip and extract everything into %s, then add that folder "
                       "to RPCS3 and run this installer again."
                       % (g, os.path.join(rpcs3, "dev_hdd0", "disc", SERIAL)))
        if is_game_folder(g):
            say("Found the game in %s" % os.path.normpath(g))
            return os.path.normpath(g)
    while True:
        g = ask_path("Where is the game? Paste the folder that contains PS3_GAME:")
        if is_game_folder(g):
            return os.path.abspath(g)
        say("That folder has no PS3_GAME\\USRDIR\\EBOOT.BIN. Try again.")


# --- 3. Original files --------------------------------------------------------

def backup_originals(usrdir, work, pristine, verify):
    step("Checking and backing up the original game files")
    have_backup = all(os.path.isfile(os.path.join(pristine, rel)) and
                      os.path.getsize(os.path.join(pristine, rel)) == ORIGINAL[rel][0] for rel in ORIGINAL)
    if have_backup:
        say("Backup already in %s" % pristine)
        return
    os.makedirs(work, exist_ok=True)
    free = shutil.disk_usage(work).free
    if free < FIRST_RUN_BYTES:
        raise Stop("The work folder needs about %d GB free; there is %.1f GB."
                   % (FIRST_RUN_BYTES // 10**9, free / 1e9))
    for rel, size_sha in sorted(ORIGINAL.items()):
        src = os.path.join(usrdir, *rel.split("/"))
        dst = os.path.join(pristine, *rel.split("/"))
        if os.path.isfile(dst) and matches(dst, size_sha):
            continue
        say("  checking %s" % rel)
        if verify and not matches(src, size_sha):
            raise Stop("%s is not the original file from the Japanese release (BLJS10133).\n"
                       "If another patch was applied, restore the original game files first.\n"
                       "If you are sure your dump is good, run again with --no-verify." % src)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        say("  backing up %s" % rel)
        shutil.copy2(src, dst)


# --- 4. Decrypt the EBOOT -----------------------------------------------------

def decrypt_eboot(rpcs3, work, pristine, verify):
    step("Decrypting the EBOOT with RPCS3")
    elf = os.path.join(pristine, "EBOOT.elf")
    if os.path.isfile(elf) and os.path.getsize(elf) == EBOOT_ELF[0]:
        say("Already decrypted.")
        return
    tmp = os.path.join(work, "eboot_tmp")
    os.makedirs(tmp, exist_ok=True)
    shutil.copy2(os.path.join(pristine, "EBOOT.BIN"), os.path.join(tmp, "EBOOT.BIN"))
    try:
        subprocess.run([rpcs3_exe(rpcs3), "--decrypt", os.path.join(tmp, "EBOOT.BIN")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    except subprocess.TimeoutExpired:
        pass
    out = os.path.join(tmp, "EBOOT.elf")
    if not os.path.isfile(out):
        raise Stop("RPCS3 could not decrypt the EBOOT. Install the PS3 firmware in RPCS3 "
                   "(File > Install Firmware), check the game boots, and run this again.")
    if verify and not matches(out, EBOOT_ELF):
        raise Stop("The decrypted EBOOT is not the one this patch was made for.")
    shutil.move(out, elf)
    shutil.rmtree(tmp, ignore_errors=True)
    say("Done.")


# --- 5. Decrypt the archives --------------------------------------------------

def decrypt_archives(work):
    step("Decrypting the game archives (a few minutes)")
    dec = os.path.join(work, "dec")
    os.makedirs(dec, exist_ok=True)
    for a in ARCHIVES:
        out = os.path.join(dec, a + ".psarc")
        if os.path.isfile(out) and os.path.getsize(out) == DECRYPTED_SIZE[a]:
            say("  %s already decrypted" % a)
            continue
        run_tool([os.path.join(TOOLS, "sdat.py"), "decrypt",
                  os.path.join(work, "pristine", "USRDIR", "PSARC", a + ".psarc.sdat"), out])


# --- 6. Build -----------------------------------------------------------------

def build(work):
    step("Building the English files (several minutes)")
    out = os.path.join(work, "build")
    shutil.rmtree(out, ignore_errors=True)
    run_tool([os.path.join(TOOLS, "build.py"), "--work", work, "--out", out])
    shutil.rmtree(os.path.join(out, "tree"), ignore_errors=True)
    return out


# --- 7. Install / uninstall ---------------------------------------------------

def warn_if_update(rpcs3):
    upd = os.path.join(rpcs3, "dev_hdd0", "game", SERIAL, "USRDIR", "EBOOT.BIN")
    if os.path.isfile(upd):
        say("\nNote: a game update is installed (%s).\nRPCS3 runs the update's EBOOT instead of the "
            "patched one, so the English text may not appear. The patch is made for the "
            "un-updated game." % upd)


def deploy(args):
    run_tool([os.path.join(TOOLS, "deploy.py")] + args)


def main(argv):
    global YES

    def opt(name):
        if name in argv:
            i = argv.index(name)
            if i + 1 >= len(argv):
                raise Stop("%s needs a folder after it." % name)
            return argv[i + 1]
        return None

    YES = "--yes" in argv
    verify = "--no-verify" not in argv
    work = os.path.abspath(opt("--work") or os.path.join(os.path.expanduser("~"), "srw2og-work"))
    pristine = os.path.join(work, "pristine", "USRDIR")
    if len(work) > 80:
        # game paths inside the work folder run to ~150 characters, and
        # Windows stops at 260 unless long paths are enabled
        raise Stop("The work folder path is too long for Windows (%d characters). "
                   "Pick a shorter one with --work, for example C:\\srw2og-work." % len(work))

    say("2nd Super Robot Wars OG English patch")
    if sys.version_info < (3, 10):
        raise Stop("Python 3.10 or newer is needed; this is %d.%d." % sys.version_info[:2])
    if os.name != "nt":
        raise Stop("The installer runs on Windows only (the build uses Windows fonts).")

    rpcs3 = find_rpcs3(opt("--rpcs3"))
    game = find_game(rpcs3, opt("--game"))
    usrdir = usrdir_of(game)
    common = ["--rpcs3", rpcs3, "--pristine", pristine, "--disc", usrdir]

    if "--uninstall" in argv:
        if not os.path.isfile(os.path.join(pristine, "EBOOT.BIN")):
            raise Stop("No backup of the original files in %s, so nothing to restore from." % pristine)
        step("Restoring the original Japanese files")
        deploy(["rollback"] + common)
        say("\nThe game is back to the original Japanese release.")
        return 0

    check_packages()
    say("\nWork folder: %s" % work)
    backup_originals(usrdir, work, pristine, verify)
    decrypt_eboot(rpcs3, work, pristine, verify)
    decrypt_archives(work)
    out = build(work)
    if "--build-only" in argv:
        say("\nBuilt into %s (not installed: --build-only)." % out)
        return 0
    step("Installing into the game")
    deploy(["install", out] + common)
    warn_if_update(rpcs3)
    say("\nDone. Start the game in RPCS3; it is now in English.")
    say("If the game asks to install data, confirm with Cross. In the game's menus, Circle confirms.")
    say("To go back to Japanese, run Uninstall.bat.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Stop as e:
        say("\nStopped: %s" % e)
        sys.exit(1)
    except KeyboardInterrupt:
        say("\nCancelled.")
        sys.exit(1)
