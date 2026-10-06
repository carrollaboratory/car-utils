import ssl
import urllib.request

import pyhornedowl
from rdflib import Graph


def open_fowl2owl(url: str, ssl_no_verify=False) -> Graph:
    ssl._create_default_https_context = ssl._create_unverified_context
    if ssl_no_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    with urllib.request.urlopen(url, context=ctx) as response:
        data = response.read().decode("utf-8")

    onto = pyhornedowl.open_ontology_from_string(data)

    rdfxml = onto.save_to_string("rdf")

    g = Graph()
    g.parse(data=rdfxml, format="xml", publicID=url)

    return g


def open_owl(url: str, ssl_no_verify=False):
    if ssl_no_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    with urllib.request.urlopen(url, context=ctx) as response:
        data = response.read()

    g = Graph()
    g.parse(data=data, format="xml", publicID=url)

    return g
