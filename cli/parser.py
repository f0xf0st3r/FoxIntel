"""CLI argument parser"""

import argparse
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="foxintel",
        description="FoxIntel - Professional OSINT Intelligence Gathering Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  foxintel domain enum example.com
  foxintel email hunter john@company.com
  foxintel social search --platform twitter "John Doe"
  foxintel breach check --service haveibeenpwned email@target.com
  foxintel image osint photo.jpg
  foxintel metadata extract document.pdf

For more information, visit: https://github.com/foxfoster/foxintel
        """
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument("-o", "--output", choices=["json", "yaml", "text", "csv"], default="json", help="Output format")
    parser.add_argument("-f", "--output-file", help="Output to file")
    parser.add_argument("-t", "--timeout", type=int, default=30, help="Request timeout (seconds)")
    parser.add_argument("-r", "--rate-limit", type=int, default=10, help="Rate limit (requests/sec)")
    parser.add_argument("--tor", action="store_true", help="Route through Tor")
    parser.add_argument("--api-key", help="Set API key (service:value)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    _add_domain_commands(subparsers)
    _add_email_commands(subparsers)
    _add_social_commands(subparsers)
    _add_breach_commands(subparsers)
    _add_image_commands(subparsers)
    _add_document_commands(subparsers)
    _add_metadata_commands(subparsers)
    _add_darkweb_commands(subparsers)
    _add_geo_commands(subparsers)
    _add_wireless_commands(subparsers)

    return parser


def _add_domain_commands(subparsers):
    domain_parser = subparsers.add_parser("domain", help="Domain intelligence gathering")
    domain_subparsers = domain_parser.add_subparsers(dest="domain_command", required=True)

    enum = domain_subparsers.add_parser("enum", help="Enumerate subdomains")
    enum.add_argument("domain", help="Target domain")
    enum.add_argument("-o", "--output", help="Output file")
    enum.add_argument("--brute", action="store_true", help="Enable DNS brute forcing")
    enum.add_argument("--passive", action="store_true", help="Passive enumeration only")

    whois = domain_subparsers.add_parser("whois", help="WHOIS lookup")
    whois.add_argument("domain", help="Target domain")
    whois.add_argument("-o", "--output", help="Output file")

    dns = domain_subparsers.add_parser("dns", help="DNS record enumeration")
    dns.add_argument("domain", help="Target domain")
    dns.add_argument("-t", "--type", default="A", help="DNS record type (A, AAAA, MX, NS, TXT, etc.)")
    dns.add_argument("-o", "--output", help="Output file")

    ip = domain_subparsers.add_parser("ip", help="IP intelligence")
    ip.add_argument("domain", help="Target domain")
    ip.add_argument("-o", "--output", help="Output file")

    ssl = domain_subparsers.add_parser("ssl", help="SSL/TLS certificate analysis")
    ssl.add_argument("domain", help="Target domain")
    ssl.add_argument("-o", "--output", help="Output file")

    takeover = domain_subparsers.add_parser("takeover", help="Subdomain takeover detection")
    takeover.add_argument("domain", help="Target domain")
    takeover.add_argument("-o", "--output", help="Output file")


def _add_email_commands(subparsers):
    email_parser = subparsers.add_parser("email", help="Email intelligence")
    email_subparsers = email_parser.add_subparsers(dest="email_command", required=True)

    hunter = email_subparsers.add_parser("hunter", help="Email discovery via Hunter.io")
    hunter.add_argument("email", help="Email address or domain")
    hunter.add_argument("-o", "--output", help="Output file")

    breach = email_subparsers.add_parser("breach", help="Check email for breaches")
    breach.add_argument("email", help="Email address")
    breach.add_argument("-s", "--service", choices=["hibp", "dehashed", "sherlock"], help="Breach service")
    breach.add_argument("-o", "--output", help="Output file")

    format = email_subparsers.add_parser("format", help="Find email format patterns")
    format.add_argument("domain", help="Target domain")
    format.add_argument("-o", "--output", help="Output file")

    verify = email_subparsers.add_parser("verify", help="Verify email deliverability")
    verify.add_argument("email", help="Email address")
    verify.add_argument("-o", "--output", help="Output file")


def _add_social_commands(subparsers):
    social_parser = subparsers.add_parser("social", help="Social media intelligence")
    social_subparsers = social_parser.add_subparsers(dest="social_command", required=True)

    search = social_subparsers.add_parser("search", help="Search across social platforms")
    search.add_argument("query", help="Search query")
    search.add_argument("-p", "--platform", choices=["twitter", "instagram", "linkedin", "facebook", "github", "all"], default="all")
    search.add_argument("-o", "--output", help="Output file")

    username = social_subparsers.add_parser("username", help="Username intelligence")
    username.add_argument("username", help="Username to search")
    username.add_argument("-p", "--platforms", nargs="+", help="Specific platforms")
    username.add_argument("-o", "--output", help="Output file")

    scrape = social_subparsers.add_parser("scrape", help="Profile scraping")
    scrape.add_argument("platform", help="Platform name")
    scrape.add_argument("username", help="Profile username")
    scrape.add_argument("-o", "--output", help="Output file")


def _add_breach_commands(subparsers):
    breach_parser = subparsers.add_parser("breach", help="Breach data intelligence")
    breach_subparsers = breach_parser.add_subparsers(dest="breach_command", required=True)

    check = breach_subparsers.add_parser("check", help="Check breach databases")
    check.add_argument("query", help="Email, domain, or username")
    check.add_argument("-s", "--service", choices=["hibp", "dehashed", "leakcheck", "snus"], help="Breach service")
    check.add_argument("-o", "--output", help="Output file")

    search = breach_subparsers.add_parser("search", help="Search breach data")
    search.add_argument("query", help="Search query")
    search.add_argument("-o", "--output", help="Output file")

    paste = breach_subparsers.add_parser("paste", help="Check paste sites")
    paste.add_argument("email", help="Email address")
    paste.add_argument("-o", "--output", help="Output file")


def _add_image_commands(subparsers):
    image_parser = subparsers.add_parser("image", help="Image OSINT")
    image_subparsers = image_parser.add_subparsers(dest="image_command", required=True)

    osint = image_subparsers.add_parser("osint", help="Reverse image search")
    osint.add_argument("image", help="Image file path or URL")
    osint.add_argument("-o", "--output", help="Output file")

    exif = image_subparsers.add_parser("exif", help="Extract EXIF data")
    exif.add_argument("image", help="Image file path")
    exif.add_argument("-o", "--output", help="Output file")

    hash = image_subparsers.add_parser("hash", help="Calculate image hashes")
    hash.add_argument("image", help="Image file path")
    hash.add_argument("-o", "--output", help="Output file")

    compare = image_subparsers.add_parser("compare", help="Compare images")
    compare.add_argument("image1", help="First image")
    compare.add_argument("image2", help="Second image")


def _add_document_commands(subparsers):
    doc_parser = subparsers.add_parser("document", help="Document intelligence")
    doc_subparsers = doc_parser.add_subparsers(dest="doc_command", required=True)

    extract = doc_subparsers.add_parser("extract", help="Extract document metadata")
    extract.add_argument("file", help="Document file path")
    extract.add_argument("-o", "--output", help="Output file")

    pdf = doc_subparsers.add_parser("pdf", help="PDF analysis")
    pdf.add_argument("file", help="PDF file path")
    pdf.add_argument("-o", "--output", help="Output file")

    office = doc_subparsers.add_parser("office", help="Office document analysis")
    office.add_argument("file", help="Office document path")
    office.add_argument("-o", "--output", help="Output file")


def _add_metadata_commands(subparsers):
    meta_parser = subparsers.add_parser("metadata", help="Metadata extraction")
    meta_subparsers = meta_parser.add_subparsers(dest="meta_command", required=True)

    extract = meta_subparsers.add_parser("extract", help="Extract metadata from file")
    extract.add_argument("file", help="File path")
    extract.add_argument("-o", "--output", help="Output file")

    parse = meta_subparsers.add_parser("parse", help="Parse metadata from URL")
    parse.add_argument("url", help="URL to parse")
    parse.add_argument("-o", "--output", help="Output file")


def _add_darkweb_commands(subparsers):
    dw_parser = subparsers.add_parser("darkweb", help="Dark web intelligence")
    dw_subparsers = dw_parser.add_subparsers(dest="dw_command", required=True)

    search = dw_subparsers.add_parser("search", help="Search dark web")
    search.add_argument("query", help="Search query")
    search.add_argument("-o", "--output", help="Output file")

    leak = dw_subparsers.add_parser("leak", help="Search leaked databases")
    leak.add_argument("query", help="Email or domain")
    leak.add_argument("-o", "--output", help="Output file")


def _add_geo_commands(subparsers):
    geo_parser = subparsers.add_parser("geo", help="Geolocation intelligence")
    geo_subparsers = geo_parser.add_subparsers(dest="geo_command", required=True)

    ip = geo_subparsers.add_parser("ip", help="IP geolocation")
    ip.add_argument("ip", help="IP address")
    ip.add_argument("-o", "--output", help="Output file")

    wifi = geo_subparsers.add_parser("wifi", help="WiFi geolocation")
    wifi.add_argument("bssid", help="BSSID (MAC address)")
    wifi.add_argument("-o", "--output", help="Output file")

    coords = geo_subparsers.add_parser("coords", help="Coordinates intelligence")
    coords.add_argument("lat", type=float, help="Latitude")
    coords.add_argument("lon", type=float, help="Longitude")
    coords.add_argument("-o", "--output", help="Output file")


def _add_wireless_commands(subparsers):
    wifi_parser = subparsers.add_parser("wireless", help="Wireless network intelligence")
    wifi_subparsers = wifi_parser.add_subparsers(dest="wifi_command", required=True)

    ap = wifi_subparsers.add_parser("ap", help="Access point lookup")
    ap.add_argument("mac", help="AP MAC address (BSSID)")
    ap.add_argument("-o", "--output", help="Output file")

    ssid = wifi_subparsers.add_parser("ssid", help="SSID lookup")
    ssid.add_argument("ssid", help="WiFi SSID name")
    ssid.add_argument("-o", "--output", help="Output file")