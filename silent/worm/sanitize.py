import re
import io
import requests
import PyPDF2
import numpy as np
from bs4 import BeautifulSoup


func_sanitize_arXiv = {
    "name": "sanitize_arXiv",
    "description": "scrapes an arXiv.org PDF, it returns just plain text.",
    "parameters": {
        "type": "object",
        "properties": {
            "properties": {
                "url": {
                    "type": "string",
                    "description": "arXiv.org PDF url to be scraped and sanitized",
                },
            },
        },
        "required": ["url"],
    },
}


def sanitize_arXiv(url, max_words=32000):
    response = requests.get(url)
    file = io.BytesIO(response.content)
    pdf = PyPDF2.PdfReader(file)
    sanitized = []
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            sanitized += page_text.split()
            break

    if len(sanitized) > max_words:
        sanitized = sanitized[0:max_words]
    return " ".join(sanitized)


func_sanitize_url = {
    "name": "sanitize_url",
    "description": "requests url and sanitizes response based on a desired set of html tags",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "url to be scraped and sanitized",
            },
            "desired_tags": {
                "type": "string",
                "description": "array of strings, values are the desired html tags to be scraped from the page",
            },
        },
        "required": ["url", "desired_tags"],
    },
}


def sanitize_url(url, desired_tags=["h1", "h2", "p", "code"], max_words=32000):
    response = requests.get(url)
    # look into html5lib too
    bucket = BeautifulSoup(response.content, "html.parser")
    sanitized = []
    for tag in desired_tags:
        for page_element in bucket.find_all(tag):
            page_text = " ".join(page_element.stripped_strings)
            formatted = re.sub(r"\W", " ", page_text)
            sanitized.append(formatted)
    if len(sanitized) > max_words:
        sanitized = sanitized[0:max_words]
    return " ".join(sanitized)
