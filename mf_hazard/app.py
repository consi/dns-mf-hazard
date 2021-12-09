import argparse
import logging

import dns.exception
import dns.resolver
import requests
from bs4 import BeautifulSoup
from rich.logging import RichHandler


def main():
    # Setup logging
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    log = logging.getLogger("dns-mf-hazard")
    log.info(
        "dns-mf-hazard - Tool to check if your DNS comply to Polish Ministry of Finance gambling domains restrictions"
    )
    # Setup global argument parser and subparser constructor
    parser = argparse.ArgumentParser(
        description="dns-mf-hazard - Tool to check if your DNS comply to Polish Ministry of Finance gambling domains restrictions"
    )
    parser.add_argument(
        "-d",
        "--dns",
        type=str,
        help="IP address of your DNS server",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--mf-ip",
        help="IP address that gambling domain should resolve",
        required=False,
        default="145.237.235.240",
    )
    # Parse arguments
    args = parser.parse_args()
    # Setup resolver
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [args.dns]
    # dict of zones with idna translation
    zones_dict = {}
    # Download list of zones from mf.gov.pl
    log.info("Downloading list of gambling domains from hazard.mf.gov.pl")
    zones_xml = requests.get("https://hazard.mf.gov.pl/api/Register")
    soup = BeautifulSoup(zones_xml.content, "lxml-xml")
    for domain in soup.findAll("AdresDomeny"):
        zones_dict[domain.string] = domain.string.encode("idna")
    log.info("Download done *{domains}* domains found.".format(domains=len(zones_dict)))
    # Print info about parsed content
    good_domains = 0
    bad_domains = 0
    for domain in zones_dict.keys():
        try:
            domain_status = check_domain(domain, args.mf_ip, resolver)
        except dns.exception.DNSException:
            log.error(
                "Domain not properly filtered because query failed, check it manually!: {} (IDNA: {})".format(
                    domain, zones_dict[domain].decode("utf-8")
                )
            )
            bad_domains += 1
            continue
        if not check_domain(domain, args.mf_ip, resolver):
            log.error(
                "Domain not properly filtered!: {} (IDNA: {})".format(
                    domain, zones_dict[domain].decode("utf-8")
                )
            )
            bad_domains += 1
        else:
            log.info(
                "Domain filtered: {} (IDNA: {})".format(
                    domain, zones_dict[domain].decode("utf-8")
                )
            )
            good_domains += 1
    if bad_domains > 0:
        log.error(
            "Your DNS server does not comply with Ministry of Finance rules. Detected bad domains: {} Good domains: {}".format(
                bad_domains, good_domains
            )
        )
    else:
        log.info(
            "Your DNS server is compliant to Ministry of Finance rules. Detected bad domains: {} Good domains: {}".format(
                bad_domains, good_domains
            )
        )


def check_domain(domain, mf_host, resolver):
    if mf_host in [ns.to_text() for ns in resolver.query(domain)]:
        return True
    return False
