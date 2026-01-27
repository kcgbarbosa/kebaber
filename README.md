# kebaber

[![Python](https://img.shields.io/badge/python-3.13+-3670A0?style=flat&logo=python&logoColor=ffdd43)](#)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](#)

Realized my file names were brutal. Here's a CLI tool to fix them. It’s safe and has pretty colours.

---

## Install & Run

```bash
git clone https://github.com/kcgbarbosa/kebaber.git
cd kebaber
python kebaber.py <path-to-folder>
```

---

## Instructions

1. Point kebaber at any folder:  
   `python kebaber.py ~/Desktop/stuff`

2. Preview loads instantly.  
   - `m` – switch Conservative ↔ Smart  
   - `a` – apply changes (asks y/n first)  
   - `q` – bail out

3. Collisions are skipped and reported; colours make it obvious what’s changing.

---

## What It Does

| Mode | What it changes |
|------|-----------------|
| **Conservative** | lowercase, spaces/underscores → hyphens |
| **Smart** | above + camelCase & letter-number splits |

Also: collision detection, confirmation prompt, colours.

---

## Examples

```bash
# Before
MyFile 2024.txt
scan-02:03:2025.pdf
IMG_1234.JPG

# After (Conservative)
myfile-2024.txt
scan-02-03-2025.pdf
img-1234.jpg

# After (Smart)
my-file-2024.txt
scan-02-03-2025.pdf
img-1234.jpg
```

## License

This is open source and available under the [MIT License](LICENSE).

