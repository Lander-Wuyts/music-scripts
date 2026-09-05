# music-scripts

Scripts for keeping a local MP3 collection tidy on Windows.

```
rename/                    Python package: renames files to the convention
old_powershell_scripts/    the original PowerShell versions
```

The Python port is the way forward; the PowerShell scripts are kept because
`fix-metadata` has not been ported yet.

## Naming convention

Every track should end up as:

```
Artist - Title.mp3
```

The separator is a space-hyphen-space (` - `), and the same values must be written into the
file's ID3 metadata:

| Field  | Value                            |
|--------|----------------------------------|
| Artist | everything before the first ` - ` |
| Title  | everything after the first ` - `, without the `.mp3` extension |

The filename is the source of truth: `rename` fixes the name, then `fix-metadata.ps1` copies the
name into the tags.

## `rename`

Bulk-renames the MP3s of a single band/album folder by prefixing the band name and stripping a
fixed-length prefix (track numbers, release tags, etc.) from the original filename.

```powershell
python -m rename -n "<band name>" -s <nr> [-e] [-d <folder>]
```

Run it from the repository root, so that `python` can find the `rename` package.

| Flag | Meaning |
|------|---------|
| `-n`, `--name` | Band name. Used as the `Artist` prefix, and as the folder name under the default root. Required. |
| `-s`, `--strip` | Number of leading characters to strip from each original filename. Required. |
| `-e`, `--execute` | Execute. Without it the script only prints the planned renames (test mode). |
| `-d`, `--directory` | Folder holding the MP3 files. Defaults to `E:\Torrents\<name>`. |

Example: with files named `01. Bohemian Rhapsody.mp3`, `-s 4` strips `01. ` and `-n "Queen"`
yields `Queen - Bohemian Rhapsody.mp3`.

```powershell
python -m rename -n "Queen" -s 4                          # dry run
python -m rename -n "Queen" -s 4 -e                       # do it
python -m rename -n "Arctic Monkeys" -s 3 -d "E:\Torrents\AM (2013)"
```

Always run once without `-e` to check the substring length before doing the real rename.

Files are left alone, with a reason printed, when they already start with `<band> - `, when
`--strip` would consume the whole name, or when the new name is already taken. Re-running is
therefore safe: a file that is already correct is never renamed twice.

Exit codes: `0` success, `1` the folder does not exist or holds no MP3s, `2` bad arguments.

### Package layout

| Module | Contents |
|--------|----------|
| `rename/__init__.py` | Public API — re-exports the functions below. |
| `rename/__main__.py` | Entry point for `python -m rename`. |
| `rename/cli.py` | Argument parsing and console output. |
| `rename/core.py` | Filename logic, no printing: `plan_renames()` works out what would change, `apply_renames()` performs it. |

The split means a dry run and a real run share one code path — the only difference is whether
`apply_renames()` gets called. The logic can also be driven from another script:

```python
from pathlib import Path
from rename import plan_renames, apply_renames

plan = plan_renames(Path(r"E:\Torrents\Queen"), "Queen", 4)
apply_renames([entry for entry in plan if not entry.skipped])
```

## Running the Python scripts on Windows

### One-time setup

- Python 3.9+ ([python.org](https://www.python.org/downloads/windows/); tick *Add python.exe to
  PATH* in the installer).
- Open PowerShell in this folder and create the virtual environment:

  ```powershell
  python -m venv .venv
  ```

  If `python` is not recognised, either re-run the installer with *Add python.exe to PATH*
  ticked, or use the launcher: `py -3 -m venv .venv`.

### Running

Two options — pick one and stick with it.

**Without activating** (simplest, no execution-policy fuss):

```powershell
.\.venv\Scripts\python.exe -m rename -n "Queen" -s 4
```

**With activation**, if you prefer a plain `python`:

```powershell
Set-ExecutionPolicy Unrestricted -Scope Process
.\.venv\Scripts\Activate.ps1
python -m rename -n "Queen" -s 4
deactivate
```

`Activate.ps1` is blocked by the default execution policy, which is why the `Set-ExecutionPolicy`
line comes first — the same one the PowerShell scripts need. It applies to the current window only.

### Dependencies

`rename` needs nothing beyond the standard library, so the venv is optional today — but it gives
the `fix-metadata` port somewhere to install [mutagen](https://mutagen.readthedocs.io/) later.
Once a package is needed:

```powershell
.\.venv\Scripts\pip.exe install mutagen
.\.venv\Scripts\pip.exe freeze > requirements.txt
```

On another machine, restore with `.\.venv\Scripts\pip.exe install -r requirements.txt`.

### Paths

Windows paths in arguments are fine as-is; quote anything containing spaces:

```powershell
python -m rename -n "Arctic Monkeys" -s 3 -d "E:\Torrents\AM (2013)"
```

Avoid a trailing backslash inside quotes — `-d "E:\Torrents\Queen\"`. Windows reads the closing
`\"` as an escaped quote, so the path arrives with a stray `"` on the end. `rename` strips it
again, but tab completion adds that backslash for you, so it is worth knowing why the path in an
error message looks odd. A trailing backslash without quotes is harmless.

## PowerShell scripts

These live in `old_powershell_scripts\` and still need:

- Windows PowerShell
- [powershell-taglib](https://github.com/illearth/powershell-taglib) — provides the `set-artist`
  and `set-title` cmdlets used by the metadata scripts.
- Because the scripts are unsigned, start each session with:

  ```powershell
  Set-ExecutionPolicy Unrestricted -Scope Process
  ```

### `fix-metadata.ps1`

Walks a playlist folder recursively and writes the artist and title tags derived from each
filename. Only files modified *after* `$last_date_modified` are touched, so re-runs stay cheap.

Settings live at the top of the script:

| Variable              | Purpose |
|-----------------------|---------|
| `$directory`          | Playlist root, searched recursively (currently `My playlist\`). |
| `$last_date_modified` | Cut-off date (`yyyy-MM-dd`); files older than this are skipped. |
| `$testing`            | `$true` short-circuits the script without touching files. |

The script lists the files it intends to change and asks for confirmation before writing. After a
run it reminds you to bump `$last_date_modified` to today's date — do that, otherwise the next run
reprocesses everything again.

### `fix-metadata-musix-box.ps1`

Variant of `fix-metadata.ps1` for the `Music Box\` folder, where the artist is not part of the
filename. It forces the artist tag to the literal `"Music Box"` and takes only the title from the
filename. Non-recursive, and it compares the modified date for *inequality* rather than using a
cut-off, so its `$last_date_modified` behaves differently from the main script.

### `rename.ps1`

Superseded by `python -m rename`. Same flags (`-n`, `-s`, `-e`), but the source folder is
hard-coded in `$directory`, and it has no skip handling — it will happily rename a file that was
already correct.

## Typical workflow

1. Download an album into `E:\Torrents\<band>\`.
2. Dry-run `python -m rename -n "<band>" -s <nr>`, verify the output, then re-run with `-e`.
3. Move the renamed files into the playlist folder.
4. Run `fix-metadata.ps1`, confirm the file list, and let it write the tags.
5. Update `$last_date_modified` in `fix-metadata.ps1` to today's date.

## Notes

- Both metadata scripts locate the separator with `IndexOf("-")`, i.e. the *first* hyphen in the
  filename. A hyphen inside the artist name will split the title in the wrong place. The Python
  `rename` package does not have this problem, as it only ever writes the separator.
