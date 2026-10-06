import ssl
import urllib.request
from pathlib import Path

import pyhornedowl
from rdflib import Graph


def save_fowl2owl(url: str, output_filepath: Path):
    """Converts an OWL2 Functional-Style Syntax file to RDF/XML format and saves it at user-specified location.
    Args:
        url: The URL of the OWL file to be converted to RDF/XML.
        output_filepath: The filepath for saving the converted file.
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8")

    onto = pyhornedowl.open_ontology_from_string(data)
    onto.save_to_file(str(output_filepath))


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


def save_owl(url: str, output_filepath: Path):
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8")
    onto = pyhornedowl.open_ontology_from_string(data)
    onto.save_to_file(str(output_filepath))


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
