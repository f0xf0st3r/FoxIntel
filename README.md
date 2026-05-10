# FoxIntel - Professional OSINT Intelligence Gathering Tool

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**FoxIntel** is a powerful, modular OSINT (Open Source Intelligence) command-line tool designed for security professionals, researchers, and penetration testers.

---

## 🚀 Quick Start

### 1. Install
```bash
git clone https://github.com/f0xf0st3r/FoxIntel.git
cd FoxIntel
pip install -r requirements.txt
```

### 2. Test
```bash
python -m main --help
```

### 3. Use Examples
```bash
# Domain enumeration
python -m main domain enum example.com

# DNS lookup
python -m main domain dns example.com -t A

# Email verification
python -m main email verify test@example.com

# IP geolocation
python -m main geo ip 8.8.8.8
```

---

## 📋 Available Commands

### 🔍 Domain Intelligence
| Command | Description |
|---------|-------------|
| `domain enum <domain>` | Enumerate subdomains |
| `domain whois <domain>` | WHOIS lookup |
| `domain dns <domain>` | DNS record enumeration |
| `domain ip <domain>` | IP intelligence |
| `domain ssl <domain>` | SSL certificate analysis |
| `domain takeover <domain>` | Subdomain takeover detection |

### 📧 Email Intelligence
| Command | Description |
|---------|-------------|
| `email verify <email>` | Verify email deliverability |
| `email breach <email>` | Check breach databases |
| `email format <domain>` | Find email patterns |
| `email hunter <email>` | Hunter.io search |

### 📱 Social Media OSINT
| Command | Description |
|---------|-------------|
| `social username <user>` | Search username across platforms |
| `social search <query>` | Search social media |
| `social scrape <platform> <user>` | Profile scraping |

### 🔓 Breach Investigation
| Command | Description |
|---------|-------------|
| `breach check <query>` | Check breach databases |
| `breach paste <email>` | Search paste sites |

### 🖼️ Image OSINT
| Command | Description |
|---------|-------------|
| `image exif <file>` | Extract EXIF metadata |
| `image osint <image>` | Reverse image search |
| `image hash <file>` | Calculate image hashes |

### 📍 Geolocation
| Command | Description |
|---------|-------------|
| `geo ip <ip>` | IP geolocation |
| `geo coords <lat> <lon>` | Coordinate analysis |
| `geo wifi <bssid>` | WiFi geolocation |

### 📄 Document Analysis
| Command | Description |
|---------|-------------|
| `document extract <file>` | Extract metadata |
| `document pdf <file>` | PDF analysis |
| `document office <file>` | Office document analysis |

---

## ⚙️ Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output format: json, yaml, text, csv |
| `-f, --output-file` | Save output to file |
| `-t, --timeout` | Request timeout (seconds) |
| `-r, --rate-limit` | Rate limit (requests/sec) |
| `--tor` | Route through Tor |
| `-d, --debug` | Debug mode |
| `-v, --verbose` | Verbose output |

---

## 📦 Installation Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- python-whois
- dnspython
- requests
- Pillow
- imagehash
- PyPDF2
- python-docx
- python-pptx
- openpyxl
- pyyaml
- beautifulsoup4
- lxml

---

## 🛡️ Disclaimer

**FoxIntel** is designed for authorized security testing and research only. Always obtain proper authorization before scanning any target. The developers are not responsible for misuse of this tool.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**f0xf0st3r** - [GitHub](https://github.com/f0xf0st3r)

---

## ⭐ Support

If this tool helped you, give it a star on GitHub!

⭐⭐⭐⭐⭐