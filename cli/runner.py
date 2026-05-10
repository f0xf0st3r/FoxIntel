"""CLI command runner"""

import json
from core.config import Config
from core.logger import FoxIntelLogger
from core.exceptions import FoxIntelError
from modules.domain.enumerator import DomainEnumerator
from modules.domain.whois_lookup import WhoisLookup
from modules.domain.dns_enum import DNSEnumerator
from modules.domain.ip_lookup import IPLookup
from modules.domain.ssl_analyzer import SSLAnalyzer
from modules.domain.takeover import TakeoverDetector
from modules.email.hunter import HunterClient
from modules.email.breach_check import BreachChecker
from modules.email.format import EmailFormatFinder
from modules.email.verify import EmailVerifier
from modules.social.search import SocialSearcher
from modules.social.username import UsernameSearcher
from modules.social.scraper import ProfileScraper
from modules.breach.checker import BreachDataChecker
from modules.breach.searcher import BreachSearcher
from modules.breach.paste import PasteSearcher
from modules.image.osint import ImageOSINT
from modules.image.exif import EXIFExtractor
from modules.image.hasher import ImageHasher
from modules.document.metadata import MetadataExtractor
from modules.document.pdf import PDFAnalyzer
from modules.document.office import OfficeAnalyzer
from modules.metadata.extractor import GenericMetadataExtractor
from modules.metadata.parser import URLMetadataParser
from modules.darkweb.search import DarkWebSearcher
from modules.darkweb.leak import LeakSearcher
from modules.geolocation.ip_geo import IPGeolocator
from modules.geolocation.wifi_geo import WiFiGeolocator
from modules.geolocation.coords import CoordinateIntelligence
from modules.wireless.ap import AccessPointLookup
from modules.wireless.ssid import SSIDLookup


class CommandRunner:
    def __init__(self, config: Config, logger: FoxIntelLogger):
        self.config = config
        self.logger = logger

    def execute(self, args) -> bool:
        command = getattr(args, 'command', None)
        subcommand = getattr(args, f'{command}_command', None)

        if command is None:
            return True

        self.logger.info(f"Executing {command} {subcommand}")

        try:
            result = self._dispatch(command, subcommand, args)
            self._output(result)
            return True
        except FoxIntelError as e:
            self.logger.error(str(e))
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if self.config.debug:
                import traceback
                traceback.print_exc()
            return False

    def _dispatch(self, command: str, subcommand: str, args) -> dict:
        handler_map = {
            ('domain', 'enum'): lambda a: DomainEnumerator(self.config, self.logger).enumerate(a.domain, brute=a.brute, passive=a.passive),
            ('domain', 'whois'): lambda a: WhoisLookup(self.config, self.logger).lookup(a.domain),
            ('domain', 'dns'): lambda a: DNSEnumerator(self.config, self.logger).enumerate(a.domain, getattr(a, 'type', 'A')),
            ('domain', 'ip'): lambda a: IPLookup(self.config, self.logger).lookup(a.domain),
            ('domain', 'ssl'): lambda a: SSLAnalyzer(self.config, self.logger).analyze(a.domain),
            ('domain', 'takeover'): lambda a: TakeoverDetector(self.config, self.logger).detect(a.domain),
            ('email', 'hunter'): lambda a: HunterClient(self.config, self.logger).search(a.email),
            ('email', 'breach'): lambda a: BreachChecker(self.config, self.logger).check(a.email, getattr(a, 'service', 'hibp')),
            ('email', 'format'): lambda a: EmailFormatFinder(self.config, self.logger).find(a.domain),
            ('email', 'verify'): lambda a: EmailVerifier(self.config, self.logger).verify(a.email),
            ('social', 'search'): lambda a: SocialSearcher(self.config, self.logger).search(a.query, getattr(a, 'platform', 'all')),
            ('social', 'username'): lambda a: UsernameSearcher(self.config, self.logger).search(a.username, getattr(a, 'platforms', None)),
            ('social', 'scrape'): lambda a: ProfileScraper(self.config, self.logger).scrape(a.platform, a.username),
            ('breach', 'check'): lambda a: BreachDataChecker(self.config, self.logger).check(a.query, getattr(a, 'service', None)),
            ('breach', 'search'): lambda a: BreachSearcher(self.config, self.logger).search(a.query),
            ('breach', 'paste'): lambda a: PasteSearcher(self.config, self.logger).search(a.email),
            ('image', 'osint'): lambda a: ImageOSINT(self.config, self.logger).search(a.image),
            ('image', 'exif'): lambda a: EXIFExtractor(self.config, self.logger).extract(a.image),
            ('image', 'hash'): lambda a: ImageHasher(self.config, self.logger).hash(a.image),
            ('document', 'extract'): lambda a: MetadataExtractor(self.config, self.logger).extract(a.file),
            ('document', 'pdf'): lambda a: PDFAnalyzer(self.config, self.logger).analyze(a.file),
            ('document', 'office'): lambda a: OfficeAnalyzer(self.config, self.logger).analyze(a.file),
            ('metadata', 'extract'): lambda a: GenericMetadataExtractor(self.config, self.logger).extract(a.file),
            ('metadata', 'parse'): lambda a: URLMetadataParser(self.config, self.logger).parse(a.url),
            ('darkweb', 'search'): lambda a: DarkWebSearcher(self.config, self.logger).search(a.query),
            ('darkweb', 'leak'): lambda a: LeakSearcher(self.config, self.logger).search(a.query),
            ('geo', 'ip'): lambda a: IPGeolocator(self.config, self.logger).locate(a.ip),
            ('geo', 'wifi'): lambda a: WiFiGeolocator(self.config, self.logger).locate(a.bssid),
            ('geo', 'coords'): lambda a: CoordinateIntelligence(self.config, self.logger).analyze(float(a.lat), float(a.lon)),
            ('wireless', 'ap'): lambda a: AccessPointLookup(self.config, self.logger).lookup(a.mac),
            ('wireless', 'ssid'): lambda a: SSIDLookup(self.config, self.logger).lookup(a.ssid),
        }

        handler = handler_map.get((command, subcommand))
        if handler:
            return handler(args)
        return {"error": f"Unknown command: {command} {subcommand}"}

    def _output(self, result: dict):
        output = json.dumps(result, indent=2, default=str)

        if self.config.output_file:
            with open(self.config.output_file, 'w') as f:
                f.write(output)
            self.logger.info(f"Results saved to {self.config.output_file}")
        else:
            print(output)