#!/usr/bin/env bash
# A-Maze-ing Defense Tester
# Kullanim: ./defense_tester.sh [repo_path] [output_validator.py]
#   repo_path           : Eval edilecek reponun yolu (default: ./42Ist-A-Maze-ing)
#   output_validator.py : PDF ekindeki validator (opsiyonel, varsa output check'i guclendirir)
#
# Tester sirayla PDF'teki her degerlendirme maddesini gezer.
# - [AUTO]  : Otomatik kontrol, PASS/FAIL otomatik basar.
# - [MANUEL]: Senin gozunle bakmani gerektirir, ekrana yapilacaklari yazar.
# Her bolum sonunda devam icin Enter beklenir.

set -u

# --- Renkler -----------------------------------------------------------------
if [ -t 1 ]; then
    RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[1;34m'
    BLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
    RED=''; GRN=''; YLW=''; BLU=''; BLD=''; DIM=''; NC=''
fi

# --- Sayaclar ----------------------------------------------------------------
PASS=0
FAIL=0
WARN=0
FATAL_FAILS=()

pass() { printf "${GRN}  [PASS]${NC} %s\n" "$1"; PASS=$((PASS+1)); }
fail() { printf "${RED}  [FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL+1)); FATAL_FAILS+=("$1"); }
warn() { printf "${YLW}  [WARN]${NC} %s\n" "$1"; WARN=$((WARN+1)); }
info() { printf "${DIM}  [INFO]${NC} %s\n" "$1"; }
note() { printf "${BLU}  >${NC} %s\n" "$1"; }

section() {
    printf "\n${BLD}${BLU}============================================================${NC}\n"
    printf "${BLD}${BLU} %s${NC}\n" "$1"
    printf "${BLD}${BLU}============================================================${NC}\n"
}

wait_user() {
    printf "\n${YLW}Devam icin Enter'a bas (atlamak icin 's' + Enter)...${NC} "
    read -r REPLY
    if [ "$REPLY" = "s" ] || [ "$REPLY" = "S" ]; then
        info "Bolum atlandi."
        return 1
    fi
    return 0
}

ask_yn() {
    # ask_yn "soru"  -> 0 = yes, 1 = no
    printf "${YLW}  ?${NC} %s [y/N]: " "$1"
    read -r ANS
    case "$ANS" in
        y|Y|yes|YES) return 0 ;;
        *)           return 1 ;;
    esac
}

# --- Argumanlar --------------------------------------------------------------
REPO="${1:-./42Ist-A-Maze-ing}"
VALIDATOR="${2:-}"

if [ ! -d "$REPO" ]; then
    printf "${RED}Repo bulunamadi:${NC} %s\n" "$REPO"
    printf "Kullanim: %s [repo_path] [output_validator.py]\n" "$0"
    exit 1
fi

REPO="$(cd "$REPO" && pwd)"

printf "${BLD}A-Maze-ing Defense Tester${NC}\n"
printf "Repo    : %s\n" "$REPO"
if [ -n "$VALIDATOR" ]; then
    printf "Validator: %s\n" "$VALIDATOR"
else
    printf "Validator: ${DIM}(verilmedi - output icerigi gozle kontrol)${NC}\n"
fi

# --- 0. Cheat / Alias kontrolu ----------------------------------------------
section "0. CHEAT / ALIAS / REPO SAGLIK"

note "Asagidaki cikiyi gor, supheli alias var mi?"
alias 2>/dev/null | head -30 || true
note "Repo .git/config remote URL:"
( cd "$REPO" && git remote -v 2>/dev/null ) || warn "git remote -v calismadi"
note "Repo en son commit:"
( cd "$REPO" && git log --oneline -3 2>/dev/null ) || warn "git log calismadi"

if ask_yn "Repo gercekten degerlendirilecek kisiye ait, sus yok?"; then
    pass "Cheat/alias kontrolu temiz"
else
    fail "CHEAT/ALIAS supheli — final grade 0 (cheat flag)"
fi

wait_user || true

# --- 1. Submitted files + Norm ----------------------------------------------
section "1. SUBMITTED FILES + NORM"

REQUIRED_FILES=(
    "README.md"
    "a_maze_ing.py"
)

for f in "${REQUIRED_FILES[@]}"; do
    if [ -f "$REPO/$f" ]; then
        pass "Var: $f"
    else
        fail "EKSIK: $f"
    fi
done

# mazegen-*.tar.gz veya .whl (root ya da dist/)
TARGZ=$(find "$REPO" -maxdepth 3 -name "mazegen-*.tar.gz" 2>/dev/null | head -1)
WHL=$(find "$REPO" -maxdepth 3 -name "mazegen-*.whl" 2>/dev/null | head -1)
if [ -n "$TARGZ" ] || [ -n "$WHL" ]; then
    pass "Paket dosyasi mevcut:"
    [ -n "$TARGZ" ] && info "  tar.gz: $TARGZ"
    [ -n "$WHL" ]  && info "  whl   : $WHL"
else
    fail "EKSIK: mazegen-*.tar.gz veya .whl"
fi

# Config file: bilinen isimler veya .conf/.cfg/.txt/.ini
CONFIGS=$(find "$REPO" -maxdepth 2 -type f \( -name "config*" -o -name "*.conf" -o -name "*.cfg" -o -name "*.ini" \) ! -name "mypy.ini" ! -name ".flake8" 2>/dev/null)
if [ -n "$CONFIGS" ]; then
    pass "Konfigurasyon dosyasi bulundu:"
    echo "$CONFIGS" | while read -r c; do info "  $c"; done
    DEFAULT_CONFIG=$(echo "$CONFIGS" | head -1)
else
    fail "EKSIK: konfigurasyon dosyasi"
    DEFAULT_CONFIG=""
fi

# Paketi yeniden build edebilmek icin gereken dosyalar
if [ -f "$REPO/pyproject.toml" ] || [ -f "$REPO/setup.py" ]; then
    pass "Paket build dosyasi var (pyproject.toml/setup.py)"
else
    fail "EKSIK: pyproject.toml veya setup.py (paketi yeniden build edemezsin)"
fi

# Norm: flake8 + mypy
note ""
note "Norm kontrolu (flake8 + mypy)..."
if command -v flake8 >/dev/null 2>&1; then
    FLAKE_OUT=$(cd "$REPO" && flake8 . --exclude=.git,__pycache__,.mypy_cache,.pytest_cache,dist,build,*.egg-info 2>&1)
    if [ -z "$FLAKE_OUT" ]; then
        pass "flake8 temiz"
    else
        fail "flake8 hatalari var:"
        echo "$FLAKE_OUT" | head -10 | sed 's/^/      /'
    fi
else
    warn "flake8 yuklu degil — atlandi"
fi

if command -v mypy >/dev/null 2>&1; then
    MYPY_OUT=$(cd "$REPO" && mypy . --exclude 'tests|build|dist|.*egg-info' 2>&1)
    if echo "$MYPY_OUT" | grep -q "Success"; then
        pass "mypy temiz"
    else
        fail "mypy hatalari var:"
        echo "$MYPY_OUT" | head -10 | sed 's/^/      /'
    fi
else
    warn "mypy yuklu degil — atlandi"
fi

note ""
note "Bu maddedeki herhangi bir EKSIK = final grade 0 (PDF kurali)."

wait_user || true

# --- 2. README.md ------------------------------------------------------------
section "2. README.md KONTROL"

README="$REPO/README.md"
if [ ! -f "$README" ]; then
    fail "README.md yok"
else
    FIRST_LINE=$(head -1 "$README")
    # ilk satir italik mi: *...* veya _..._ ile basliyor mu?
    if echo "$FIRST_LINE" | grep -qE '^\*.*\*$|^_.*_$'; then
        # 'created as par' veya 'created as part' iceriyor mu?
        if echo "$FIRST_LINE" | grep -qiE 'created as par'; then
            pass "Ilk satir italik + 'created as par...' formatinda"
        else
            fail "Ilk satir italik AMA 'This project has been created as par by <login>, <login>.' formati degil"
            info "  Bulunan: $FIRST_LINE"
        fi
    else
        fail "Ilk satir italik formatinda DEGIL"
        info "  Bulunan: $FIRST_LINE"
        info "  Beklenen: *This project has been created as part of ... by login1, login2.*"
    fi

    declare -A REQ_SECTIONS=(
        ["Description"]="Description"
        ["Instructions"]="Instructions"
        ["Resources"]="Resources"
    )
    for key in "${!REQ_SECTIONS[@]}"; do
        if grep -qiE "^#+ *${REQ_SECTIONS[$key]}" "$README"; then
            pass "Section var: $key"
        else
            fail "Section EKSIK: $key"
        fi
    done

    note ""
    note "Asagidaki maddeleri README'de gozle ara (varsa Enter / yoksa hata bildir):"
    note "  - Konfigurasyon dosyasinin tam aciklamasi"
    note "  - Secilen maze algoritmasi"
    note "  - Bu algoritmanin neden secildigi"
    note "  - Reusable mazegen modulu icin kisa dokumentasyon"
    note "  - Takim uyelerinin rolleri"
    note "  - Planlanan takvim ve nasil evrildigi"
    note "  - Iyi giden + iyilestirilebilecek seyler"
    note "  - Kullanilan ozel araclar"

    if ! ask_yn "README'de yukaridaki TUM maddeler var mi?"; then
        fail "README'de zorunlu maddelerden eksik var (PDF: missing => grade 0)"
    else
        pass "README icerigi tam (gozle dogrulandi)"
    fi
fi

wait_user || true

# --- 3. STANDARD USAGE - Display --------------------------------------------
section "3. STANDARD USAGE — DISPLAY"

if [ ! -f "$REPO/a_maze_ing.py" ]; then
    fail "a_maze_ing.py yok — bu test calistirilamiyor"
else
    note "Asagidaki komutu CALISTIR (yeni terminal acabilirsin):"
    note ""
    note "    cd $REPO"
    note "    python3 a_maze_ing.py"
    note ""
    note "Beklenen: rastgele bir maze ekranda gosterildi (terminal veya grafik pencere)."
    note "Crash, traceback, beklenmeyen exit OLMAMALI."

    if ask_yn "Maze duzgun gosterildi mi (crash yok)?"; then
        pass "Display calisiyor"
    else
        fail "Display calismiyor / crash"
    fi
fi

wait_user || true

# --- 4. INTERACTIVE MENU -----------------------------------------------------
section "4. INTERACTIVE MENU"

note "Calisan programda asagidaki ETKILESIMLERIN HEPSI olmali:"
note "  1) Yeni bir maze yeniden uretme"
note "  2) Entry'den exit'e en kisa yolu goster/gizle TOGGLE"
note "  3) Duvar renklerini degistirme butonu"
note ""
note "Bunlar ZORUNLU. Ekstra etkilesimler (renkli 42, quit vs.) opsiyonel."

if ask_yn "(1) Yeni maze uretme var mi?"; then pass "Re-generate var"; else fail "Re-generate YOK"; fi
if ask_yn "(2) Shortest path toggle var mi?"; then pass "Path toggle var"; else fail "Path toggle YOK"; fi
if ask_yn "(3) Duvar rengi degistirme var mi?"; then pass "Wall color var"; else fail "Wall color YOK"; fi

wait_user || true

# --- 5. CONFIGURATION FILE FORMAT -------------------------------------------
section "5. CONFIGURATION FILE — FORMAT"

if [ -z "$DEFAULT_CONFIG" ]; then
    fail "Config dosyasi yok, format kontrolu yapilamiyor"
else
    note "Default config: $DEFAULT_CONFIG"
    note "Icerigi:"
    cat "$DEFAULT_CONFIG" | sed 's/^/      /'
    note ""

    # Comment satirlari # ile baslamali — sadece olduklarini varsay
    if grep -qE '^[[:space:]]*#' "$DEFAULT_CONFIG"; then
        pass "# ile baslayan comment satirlari var (sentaks dogru)"
    else
        info "Comment satiri yok (varsa # ile baslamali — manuel kontrol)"
    fi

    # KEY=VALUE format kontrolu (non-comment, non-empty)
    BAD=$(grep -vE '^[[:space:]]*#|^[[:space:]]*$' "$DEFAULT_CONFIG" | grep -vE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' || true)
    if [ -z "$BAD" ]; then
        pass "Tum satirlar KEY=VALUE formatinda"
    else
        fail "KEY=VALUE formatina uymayan satir var:"
        echo "$BAD" | sed 's/^/      /'
    fi

    # Zorunlu key'ler
    for k in WIDTH HEIGHT ENTRY EXIT OUTPUT_FILE PERFECT; do
        if grep -qiE "^[[:space:]]*${k}[[:space:]]*=" "$DEFAULT_CONFIG"; then
            pass "Key var: $k"
        else
            fail "Zorunlu key EKSIK: $k"
        fi
    done
fi

wait_user || true

# --- 6. ERROR MANAGEMENT (CONFIG) -------------------------------------------
section "6. CONFIG ERROR MANAGEMENT"

if [ -z "$DEFAULT_CONFIG" ]; then
    fail "Config yok, error testleri yapilamiyor"
else
    TMPDIR=$(mktemp -d)
    note "Test config'leri burada: $TMPDIR"

    BASE="$TMPDIR/base.cfg"
    cp "$DEFAULT_CONFIG" "$BASE"

    run_amazeing() {
        local cfg="$1"
        local label="$2"
        ( cd "$REPO" && timeout 10 python3 a_maze_ing.py "$cfg" 2>&1 < /dev/null )
        local rc=$?
        return $rc
    }

    test_error_case() {
        local cfg="$1"
        local label="$2"
        note ""
        note "TEST: $label"
        note "  Config dosyasi: $cfg"
        note "  Beklenen: a_maze_ing.py temiz bir hata mesaji + duzgun cikis (crash YOK)"
        note "  CALISTIR (yeni terminal):"
        note "      cd $REPO && python3 a_maze_ing.py $cfg"
        note ""
        if ask_yn "Program crash etmeden anlamli hata verdi mi?"; then
            pass "$label: hata duzgun yonetildi"
        else
            fail "$label: crash veya yetersiz hata mesaji"
        fi
    }

    # Case 1: Zorunlu key sil
    C1="$TMPDIR/no_width.cfg"
    grep -viE '^[[:space:]]*WIDTH[[:space:]]*=' "$BASE" > "$C1"
    test_error_case "$C1" "Zorunlu key (WIDTH) silinmis"

    # Case 2: '=' siz satir
    C2="$TMPDIR/no_eq.cfg"
    cp "$BASE" "$C2"
    echo "BOZUKSATIR" >> "$C2"
    test_error_case "$C2" "'=' icermeyen satir eklendi"

    # Case 3: Sayi yerine harf
    C3="$TMPDIR/letters.cfg"
    sed 's/^\([[:space:]]*WIDTH[[:space:]]*=\).*/\1abc/I' "$BASE" > "$C3"
    test_error_case "$C3" "WIDTH=abc (harfli sayi)"

    # Case 4: PERFECT'e bozuk bool
    C4="$TMPDIR/bad_perfect.cfg"
    sed 's/^\([[:space:]]*PERFECT[[:space:]]*=\).*/\1banana/I' "$BASE" > "$C4"
    test_error_case "$C4" "PERFECT=banana"

    # Case 5: ENTRY format bozuk
    C5="$TMPDIR/bad_entry.cfg"
    sed 's/^\([[:space:]]*ENTRY[[:space:]]*=\).*/\11x2/I' "$BASE" > "$C5"
    test_error_case "$C5" "ENTRY=1x2 (yanlis tuple format)"

    note ""
    note "HATIRLATMA: Yukaridaki testlerden HERHANGI BIRINDE crash olursa final grade 0."
fi

wait_user || true

# --- 7. OUTPUT FILE FORMAT --------------------------------------------------
section "7. OUTPUT FILE — FORMAT"

if [ -z "$DEFAULT_CONFIG" ]; then
    fail "Config yok, output kontrolu yapilamiyor"
else
    # OUTPUT_FILE adini config'ten cek
    OUT_NAME=$(grep -iE '^[[:space:]]*OUTPUT_FILE[[:space:]]*=' "$DEFAULT_CONFIG" | head -1 | sed -E 's/^[^=]*=[[:space:]]*//' | tr -d '"' | tr -d "'" | xargs)
    if [ -z "$OUT_NAME" ]; then
        warn "OUTPUT_FILE key bulunamadi"
    else
        info "OUTPUT_FILE: $OUT_NAME"
    fi

    WIDTH_V=$(grep -iE '^[[:space:]]*WIDTH[[:space:]]*=' "$DEFAULT_CONFIG" | head -1 | sed -E 's/^[^=]*=[[:space:]]*//' | xargs)
    HEIGHT_V=$(grep -iE '^[[:space:]]*HEIGHT[[:space:]]*=' "$DEFAULT_CONFIG" | head -1 | sed -E 's/^[^=]*=[[:space:]]*//' | xargs)
    ENTRY_V=$(grep -iE '^[[:space:]]*ENTRY[[:space:]]*=' "$DEFAULT_CONFIG" | head -1 | sed -E 's/^[^=]*=[[:space:]]*//' | xargs)
    EXIT_V=$(grep -iE '^[[:space:]]*EXIT[[:space:]]*=' "$DEFAULT_CONFIG" | head -1 | sed -E 's/^[^=]*=[[:space:]]*//' | xargs)

    note ""
    note "CALISTIR (yeni terminal):"
    note "    cd $REPO && python3 a_maze_ing.py $DEFAULT_CONFIG"
    note ""
    note "Beklenen output dosya icerigi:"
    note "  1. HEIGHT satir x WIDTH karakter hex (her satir tam WIDTH char)"
    note "  2. 1 bos satir"
    note "  3. ENTRY tuple satiri (orn: 0,0)"
    note "  4. EXIT tuple satiri  (orn: ${WIDTH_V:-W}-1,${HEIGHT_V:-H}-1)"
    note "  5. Shortest path: N/E/S/W harflerinden olusan tek satir"
    note ""

    if ask_yn "Output dosyasi olusturuldu mu?"; then
        OUT_PATH=""
        # Ortak konumlarda ara
        for cand in "$REPO/$OUT_NAME" "$OUT_NAME" "$REPO/$(basename "$OUT_NAME")"; do
            if [ -f "$cand" ]; then OUT_PATH="$cand"; break; fi
        done
        if [ -z "$OUT_PATH" ]; then
            warn "Output dosyasi otomatik bulunamadi — tam yolu gir:"
            printf "  Path: "
            read -r OUT_PATH
        fi
        if [ -f "$OUT_PATH" ]; then
            info "Bulunan output: $OUT_PATH"
            note "Output ilk satirlari:"
            head -5 "$OUT_PATH" | sed 's/^/      /'
            note "Output son satirlari:"
            tail -5 "$OUT_PATH" | sed 's/^/      /'

            # Otomatik format kontrolu (python)
            python3 - "$OUT_PATH" "${WIDTH_V:-0}" "${HEIGHT_V:-0}" "${ENTRY_V:-0,0}" "${EXIT_V:-0,0}" <<'PYEOF'
import sys, re

path = sys.argv[1]
exp_w = int(sys.argv[2]) if sys.argv[2].isdigit() else None
exp_h = int(sys.argv[3]) if sys.argv[3].isdigit() else None
exp_entry = sys.argv[4]
exp_exit  = sys.argv[5]

lines = open(path).read().splitlines()

def ok(s):   print("  [PASS]", s)
def bad(s):  print("  [FAIL]", s)

# 1) HEIGHT satir x WIDTH karakter
if exp_h is None or exp_w is None:
    print("  [INFO] WIDTH/HEIGHT okunamadi — boyut kontrolu atlandi")
else:
    grid_lines = lines[:exp_h]
    if len(grid_lines) < exp_h:
        bad(f"Output'ta {exp_h} satir bekleniyordu, {len(grid_lines)} bulundu")
    else:
        bad_rows = [(i, len(l)) for i, l in enumerate(grid_lines) if len(l) != exp_w]
        if bad_rows:
            bad(f"WIDTH karakter sayisi tutmayan satir(lar): {bad_rows[:3]}")
        else:
            ok(f"{exp_h} satir x {exp_w} hex karakter dogru")

        # Hex karakter mi?
        non_hex = [i for i, l in enumerate(grid_lines) if not re.fullmatch(r"[0-9A-Fa-f]+", l)]
        if non_hex:
            bad(f"Hex disi karakter iceren satir(lar): {non_hex[:3]}")
        else:
            ok("Tum satirlar hex karakterlerden olusuyor")

# 2) Bos satir
if exp_h is not None and len(lines) > exp_h:
    if lines[exp_h].strip() == "":
        ok("Grid'den sonra bos satir var")
    else:
        bad(f"Grid'den sonra bos satir beklenirken: {lines[exp_h]!r}")

# 3-4) ENTRY / EXIT
if exp_h is not None:
    tail = lines[exp_h+1:]
    if len(tail) >= 3:
        ent, ext, pth = tail[0], tail[1], tail[2]
        # entry/exit format
        if re.fullmatch(r"\s*\d+\s*,\s*\d+\s*", ent):
            ok(f"ENTRY satiri tuple formatinda: {ent}")
        else:
            bad(f"ENTRY satiri tuple degil: {ent!r}")
        if re.fullmatch(r"\s*\d+\s*,\s*\d+\s*", ext):
            ok(f"EXIT satiri tuple formatinda: {ext}")
        else:
            bad(f"EXIT satiri tuple degil: {ext!r}")
        if re.fullmatch(r"[NESW]+", pth):
            ok(f"PATH satiri N/E/S/W harflerinden olusuyor (uzunluk {len(pth)})")
        else:
            bad(f"PATH satiri N/E/S/W disi karakter iceriyor veya bos: {pth!r}")
    else:
        bad("Output dosyasinda ENTRY/EXIT/PATH satirlari eksik")
PYEOF

            if [ -n "$VALIDATOR" ] && [ -f "$VALIDATOR" ]; then
                note ""
                note "output_validator.py calistiriliyor..."
                if python3 "$VALIDATOR" "$OUT_PATH"; then
                    pass "validator: OK"
                else
                    fail "validator: hata"
                fi
            else
                note ""
                note "MANUEL: subject ekindeki output_validator.py'yi calistir:"
                note "    python3 output_validator.py $OUT_PATH"
                if ask_yn "Validator gecti mi (path duvarlarla tutarli)?"; then
                    pass "Path/duvar tutarliligi (validator)"
                else
                    fail "Validator hata verdi"
                fi
            fi
        else
            fail "Output dosyasi bulunamadi"
        fi
    else
        fail "Output dosyasi uretilmedi"
    fi
fi

wait_user || true

# --- 8. MAZE GENERATOR ICERIK KONTROLLERI -----------------------------------
section "8. MAZE GENERATOR — ICERIK"

# Mazegen paketini direkt python'dan test et (a_maze_ing.py'a bagimsiz).
note "Mazegen paketini dogrudan test ediyorum (PYTHONPATH=$REPO)..."

PYTHONPATH="$REPO" python3 - <<'PYEOF'
import sys, traceback

PASS, FAIL = 0, 0
def ok(s):   globals().__setitem__('PASS', PASS+1); print("  [PASS]", s)
def bad(s):  globals().__setitem__('FAIL', FAIL+1); print("  [FAIL]", s)

try:
    from mazegen import MazeGenerator, MazeSolver, Grid
except Exception as e:
    print("  [FAIL] mazegen import edilemedi:", e)
    sys.exit(1)

# Test 1: Random — ayni boyut, seed yok => farkli mazelar uretilmeli
try:
    g1 = MazeGenerator(15, 11, add_42=False); g1.generate()
    g2 = MazeGenerator(15, 11, add_42=False); g2.generate()
    if g1.to_hex_lines() != g2.to_hex_lines():
        ok("Random: ayni boyut seed=None -> farkli maze")
    else:
        bad("Random: iki maze ayni cikti (seed yokken bile)")
except Exception as e:
    bad(f"Random testi crash: {e}")

# Test 2: Seed reproducibility
try:
    g1 = MazeGenerator(15, 11, seed=42, add_42=False); g1.generate()
    g2 = MazeGenerator(15, 11, seed=42, add_42=False); g2.generate()
    if g1.to_hex_lines() == g2.to_hex_lines():
        ok("Seed: ayni seed -> ayni maze")
    else:
        bad("Seed: ayni seed -> FARKLI maze (reproducibility kirik)")
except Exception as e:
    bad(f"Seed testi crash: {e}")

# Test 3: Inkonsistens parametreler (negatif width / 0)
for w, h, label in [(-1, 10, "negatif width"), (10, 0, "sifir height"), (0, 0, "0x0")]:
    try:
        g = MazeGenerator(w, h, add_42=False)
        g.generate()
        bad(f"Inkonsistens param ({label}): exception bekleniyordu, hicbiri firlamadi")
    except Exception as e:
        ok(f"Inkonsistens param ({label}): exception firlatti ({type(e).__name__})")

# Test 4: Outer walls all closed
def outer_walls_closed(g):
    grid = g.grid
    for x in range(grid.width):
        if not grid.get(x, 0).has_wall("N"):           return False
        if not grid.get(x, grid.height-1).has_wall("S"): return False
    for y in range(grid.height):
        if not grid.get(0, y).has_wall("W"):           return False
        if not grid.get(grid.width-1, y).has_wall("E"): return False
    return True

try:
    g = MazeGenerator(20, 15, seed=1, add_42=False); g.generate()
    if outer_walls_closed(g):
        ok("Disardaki tum duvarlar kapali")
    else:
        bad("Maze etrafindaki disti duvarlar acik")
except Exception as e:
    bad(f"Outer walls testi crash: {e}")

# Test 5: All cells reachable (BFS flood fill) — 42 pattern haric
try:
    g = MazeGenerator(25, 17, seed=2, add_42=True); g.generate()
    grid = g.grid
    # baslangic icin breakable bir hucre bul
    from collections import deque
    start = None
    for y in range(grid.height):
        for x in range(grid.width):
            if not grid.get(x, y).unbreakable:
                start = (x, y); break
        if start: break
    visited = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        c = grid.get(x, y)
        for d, nc in grid.neighbors(x, y).items():
            if not c.has_wall(d) and (nc.x, nc.y) not in visited:
                visited.add((nc.x, nc.y)); q.append((nc.x, nc.y))
    breakable = sum(1 for y in range(grid.height) for x in range(grid.width) if not grid.get(x,y).unbreakable)
    if len(visited) == breakable:
        ok(f"Tum breakable hucreler erisilebilir ({len(visited)}/{breakable})")
    else:
        bad(f"Erisilemeyen hucreler var: visited={len(visited)} breakable={breakable}")
except Exception as e:
    bad(f"Reachability testi crash: {e}")
    traceback.print_exc()

# Test 6: 3x3 acik bolge YOK
try:
    g = MazeGenerator(25, 17, seed=3, add_42=False); g.generate()
    grid = g.grid
    bad_block = None
    for y in range(grid.height - 2):
        for x in range(grid.width - 2):
            # 3x3 blok icindeki TUM ic duvarlar acik mi?
            walls_open = True
            for dy in range(3):
                for dx in range(3):
                    c = grid.get(x+dx, y+dy)
                    # ic duvarlari kontrol et
                    if dx < 2 and c.has_wall("E"): walls_open = False
                    if dy < 2 and c.has_wall("S"): walls_open = False
                    if not walls_open: break
                if not walls_open: break
            if walls_open:
                bad_block = (x, y); break
        if bad_block: break
    if bad_block is None:
        ok("3x3 veya daha buyuk acik bolge yok")
    else:
        bad(f"3x3 acik bolge tespit edildi koselerde {bad_block}")
except Exception as e:
    bad(f"3x3 testi crash: {e}")

# Test 7: 42 pattern var (yeterince buyuk grid'de)
try:
    g = MazeGenerator(25, 17, seed=4, add_42=True); g.generate()
    grid = g.grid
    has_pattern = any(grid.get(x,y).is_42_pattern
                      for y in range(grid.height) for x in range(grid.width))
    if has_pattern:
        ok("42 pattern grid icinde isaretli")
    else:
        bad("42 pattern bulunamadi (grid yeterince buyuk olmasina ragmen)")
except Exception as e:
    bad(f"42 pattern testi crash: {e}")

# Test 8: Perfect maze (PERFECT=True icin uygun) — kenar sayisi = N-1
try:
    g = MazeGenerator(20, 15, seed=5, add_42=False); g.generate()
    grid = g.grid
    n_cells = grid.width * grid.height
    # acik kenar sayisi: her hucrenin acik E ve S duvarlarini say (cift sayim olmasin)
    open_edges = 0
    for y in range(grid.height):
        for x in range(grid.width):
            c = grid.get(x,y)
            if x < grid.width - 1 and not c.has_wall("E"): open_edges += 1
            if y < grid.height - 1 and not c.has_wall("S"): open_edges += 1
    # Perfect maze: acik kenar sayisi = n_cells - 1 (spanning tree)
    if open_edges == n_cells - 1:
        ok(f"Perfect maze: acik kenar={open_edges} = N-1={n_cells-1}")
    else:
        # not: 42 pattern olmasa bile bazi konfigurasyonlarda istisnalar olabilir
        bad(f"Perfect maze degil: open_edges={open_edges}, beklenen={n_cells-1}")
except Exception as e:
    bad(f"Perfect maze testi crash: {e}")

print(f"\n  Mazegen ic testler: PASS={PASS} FAIL={FAIL}")
sys.exit(0 if FAIL == 0 else 2)
PYEOF
RC=$?
if [ $RC -eq 0 ]; then
    pass "Mazegen icerik testleri (tumu)"
elif [ $RC -eq 2 ]; then
    fail "Mazegen icerik testlerinde hata var (yukariya bak)"
else
    fail "Mazegen test scripti calistirilamadi (rc=$RC)"
fi

note ""
note "MANUEL: 3x3 acik bolge kontrolu nasil implement edildigini sor:"
note '    "3x3 acik bolge olmamasini nasil garanti ediyorsun?"'

wait_user || true

# --- 9. REUSABLE MODULE (BUILD + INSTALL) -----------------------------------
section "9. REUSABLE MODULE — BUILD + INSTALL"

note "Bu adim virtualenv kullanir. Hazir misin?"
if ! ask_yn "Devam edeyim mi?"; then
    info "Reusable module testi atlandi"
else
    BUILD_DIR=$(mktemp -d)
    note "Build dizini: $BUILD_DIR"

    note ""
    note "1) Yeni venv olusturuluyor (build icin)..."
    python3 -m venv "$BUILD_DIR/venv_build"
    # shellcheck source=/dev/null
    source "$BUILD_DIR/venv_build/bin/activate"
    pip install --quiet --upgrade pip build 2>&1 | tail -3

    note ""
    note "2) Paket build ediliyor (cd $REPO && python -m build)..."
    BUILD_OUT="$BUILD_DIR/build.log"
    ( cd "$REPO" && python -m build --outdir "$BUILD_DIR/dist" ) > "$BUILD_OUT" 2>&1
    if [ $? -eq 0 ]; then
        pass "Paket build OK"
        NEW_TARGZ=$(find "$BUILD_DIR/dist" -name "mazegen-*.tar.gz" | head -1)
        NEW_WHL=$(find "$BUILD_DIR/dist" -name "mazegen-*.whl" | head -1)
        info "  tar.gz: $NEW_TARGZ"
        info "  whl   : $NEW_WHL"
    else
        fail "Paket build FAIL — log:"
        tail -15 "$BUILD_OUT" | sed 's/^/      /'
    fi
    deactivate || true

    note ""
    note "3) Yeni venv'de install edilip a_maze_ing.py calistirilacak..."
    python3 -m venv "$BUILD_DIR/venv_run"
    # shellcheck source=/dev/null
    source "$BUILD_DIR/venv_run/bin/activate"
    if [ -n "${NEW_WHL:-}" ]; then
        pip install --quiet "$NEW_WHL" 2>&1 | tail -3
        if pip show mazegen >/dev/null 2>&1; then
            pass "Paket yeni venv'e install edildi"
        else
            fail "Paket install edilemedi"
        fi
    elif [ -n "${NEW_TARGZ:-}" ]; then
        pip install --quiet "$NEW_TARGZ" 2>&1 | tail -3
        if pip show mazegen >/dev/null 2>&1; then
            pass "Paket yeni venv'e install edildi"
        else
            fail "Paket install edilemedi"
        fi
    else
        fail "Build cikti bulunamadi — install edilemiyor"
    fi

    note ""
    note "4) Bu venv'de a_maze_ing.py + config calistir:"
    note "    source $BUILD_DIR/venv_run/bin/activate"
    note "    cd $REPO && python a_maze_ing.py ${DEFAULT_CONFIG:-CONFIG_YOK}"
    note ""
    if ask_yn "Yeni venv'de program duzgun calisti mi?"; then
        pass "Reusable module end-to-end calisiyor"
    else
        fail "Reusable module end-to-end calismiyor"
    fi
    deactivate || true
fi

wait_user || true

# --- OZET --------------------------------------------------------------------
section "OZET"

printf "  ${GRN}PASS${NC}: %d\n" "$PASS"
printf "  ${RED}FAIL${NC}: %d\n" "$FAIL"
printf "  ${YLW}WARN${NC}: %d\n" "$WARN"

if [ "$FAIL" -gt 0 ]; then
    printf "\n${RED}${BLD}HATALAR:${NC}\n"
    for f in "${FATAL_FAILS[@]}"; do
        printf "  - %s\n" "$f"
    done
    printf "\n${RED}${BLD}PDF kurali:${NC} Basics'te (dosyalar/README/norm) eksik => grade 0.\n"
    printf "${RED}${BLD}PDF kurali:${NC} Defense sirasinda crash => grade 0.\n"
    exit 1
else
    printf "\n${GRN}${BLD}Tum testler gecti. DEFENSE_GUIDE.md'i bir kez daha gozden gecir, sonra sun.${NC}\n"
    exit 0
fi
