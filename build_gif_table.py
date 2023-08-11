"""
Helper functions to build the full text search database from various
    sources.
"""
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import typing
import shutil
import os
import hashlib
import time

from app.models.gif import *

from app import *

class GifFetcher:
    """
    Parent class for fetching GIFs from various sources.
    """
    GIF_PATH = appconfig["GIF_PATH"]
    CHUNK_SIZE = 256

    def iterate_gifs(self):
        """
        Stub method for iterating through GIFs. Subclasses
            must implement.
        """
        pass
    
    def save_image_stream(self, 
                          image_stream: typing.BinaryIO) -> str:
        """
        Save the image contained in the binary file-like to a file
            named for the SHA256 of the image (using "tmp" as an
            intermediary).
        :param img_stream: File-like object (supports read()) 
            containing image data
        :return: SHA256 of image, or None if image has no content
        """
        sha = hashlib.sha256()
        has_content = False
        with open(os.path.join(GIF_PATH, "tmp"), "wb") as tmpfile:
            chunk = image_stream.read(CHUNK_SIZE)
            while chunk != b"":
                has_content = True
                tmpfile.write(chunk)
                sha.update(chunk)
        if has_content:
            shutil.move(
                os.path.join(GIF_PATH, "tmp"), 
                os.path.join(GIF_PATH, sha.hexdigest())
            )
            return sha.hexdigest()
        return None


class GifCitiesFetcher(GifFetcher):
    """
    Subclass of GifFetcher for web access to GifCities GIFs.
    Gentle scraper, should be used only for small test sets of 
    GIFs (less than 1,000 queries)"
    """
    GIFCITIES_BASE_URL = "https://gifcities.org"
    GIF_ARCHIVE_BASE_URL = "https://web.archive.org/web"
    REQUEST_SLEEP = 0.5

    def __init__(self, search_file: typing.TextIO):
        """
        Constuctor for GifCities fetcher.
        :param search_file: file object containing search terms 
            (one per line)
        """
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.browser = webdriver.Firefox(options)
        self.search_file = search_file
     
    def iterate_gifs(self):
        """
        Iterator generator to save GIFS and get (image, search terms)
            pairs.
        :yield: (search terms string, image SHA256 filename) tuple
        """
        for search_term in search_file.readlines():
            browser.get(f"{GIFCITIES_BASE_URL}/?q={search_term}")
            for element in browser.find_elements(By.TAG_NAME, "img"):
                gif_uri = element.get_attribute("src")
                terms = element.get_attribute("title")
                    if gif_uri and gif_uri.startswith(
                            GIF_ARCHIVE_BASE_URL) and terms:
                        response = requests.get(
                            gif_uri, stream=True)
                        sha = self.save_image_stream(
                            response.raw
                        )
                        yield (terms, sha)
            time.sleep(REQUEST_SLEEP)

class DatabaseBuilder:
    """
    Helper class that initiates a database session, iterates through
        the provided GIF iterator, and enters each into the database.
    """
    def __init__(self, fetcher: GifFetcher, db_resource: SQLAlchemy):
        """
        Constructor for database builder object.
        :param fetcher: GifFetcher subclass containing GIF iterator
        :param db_resource: SQLALchemy database object
        """
        self.fetcher = fetcher
        self.db_resource = db_resource

    def build(self, spell_check: bool = True):
        """
        Iteratively adds GIFs and search terms to the database.
        :param spell_check: Whether to perform spell checking and
            attempt correction on the derived search terms
        """
        # TODO: build GIF mapping
