"""
Helper functions to build the full text search database from various
    sources.
"""
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.common.by import By
from spellchecker import SpellChecker
import wordninja
import requests
import typing
import shutil
import os
import hashlib
import time
import json

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
        with open(os.path.join(self.GIF_PATH, "tmp"), "wb") as tmpfile:
            chunk = image_stream.read(self.CHUNK_SIZE)
            while chunk != b"":
                has_content = True
                tmpfile.write(chunk)
                sha.update(chunk)
                chunk = image_stream.read(self.CHUNK_SIZE)
        if has_content:
            shutil.move(
                os.path.join(self.GIF_PATH, "tmp"), 
                os.path.join(self.GIF_PATH, sha.hexdigest())
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
    GIFS_PER_PAGE = 5
    PAGE_LOAD_SLEEP = 15
    REQUEST_SLEEP = 0.5
    REQUEST_TIMEOUT = 60

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
        for search_term in self.search_file.readlines():
            self.browser.get(
                f"{self.GIFCITIES_BASE_URL}/?q={search_term}")
            time.sleep(self.PAGE_LOAD_SLEEP)
            gifs = [(element.get_attribute("src"), 
                     element.get_attribute("title"))
                    for element in self.browser.find_elements(
                        By.TAG_NAME, "img")][:self.GIFS_PER_PAGE]
            for gif_uri, term_string in gifs:
                if (gif_uri and gif_uri.startswith(
                        self.GIF_ARCHIVE_BASE_URL) and term_string
                        and term_string != 
                        "Donate to the Internet Archive"):
                    try:
                        response = requests.get(
                            gif_uri, stream=True, 
                            timeout=self.REQUEST_TIMEOUT
                        )
                        sha = self.save_image_stream(
                            response.raw
                        )
                        yield (term_string, sha)
                        time.sleep(self.REQUEST_SLEEP)
                    except Exception:
                        continue

class ManifestFetcher:
    """
    Subclass of GifFetcher for building database using a manifest of 
        locally stored GIFs and their search terms
    """
    def __init__(self, manifest_file: typing.TextIO):
        """
        Constructor for manifest fetcher
        :param manifest_file: File object containing JSON manifest
            list of (term string, SHA) tuples
        """
        self.manifest = json.load(manifest_file)

    def iterate_gifs(self):
        """
        Iterator generator wrapper for manifest list
        :yield: (search terms string, image SHA256 filename) tuple
        """
        for entry in self.manifest:
            yield entry

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

    def build(self, spell_check: bool = True, 
              split_words: bool = True,
              verbose: bool = False,
              manifest_path: str = None):
        """
        Iteratively adds GIFs and search terms to the database.
        :param spell_check: Whether to perform spell checking and
            attempt correction on the derived search terms
        :param split_words: Whether to attempt to split 
            undelimeted strings into constituent words
        :param verbose: Whether to print progress
        :param manifest_path: If path provided, store a manifest
            JSON file mapping term strings to SHAs 
        """
        if spell_check:
            sc = SpellChecker()
        iterator = 0
        manifest = []
        for term_string, sha in self.fetcher.iterate_gifs():
            manifest.append((term_string, sha))
            if iterator % 10 == 0 and verbose:
                print(f"Processing GIF with SHA {sha} and " +
                      f"terms {term_string}...")
            iterator += 1
            values = [value.lower() 
                     for value in term_string.split()]
            if split_words:
                split_values = [wordninja.split(value)
                                for value in values]
                values = [value for split_value in split_values
                          for value in split_value]
            if spell_check:
                values = [sc.correction(value.lower())
                         for value in values]

            gif_obj = self.db_resource.session.get(
                Gif, sha
            )
            if not gif_obj:
                gif_obj = Gif(sha=sha)
                self.db_resource.session.add(gif_obj)
            
            for value in values:
                term_obj = self.db_resource.session.get(
                    Term, value
                )
                if not term_obj:
                    term_obj = Term(value=value)
                    self.db_resource.session.add(term_obj)
                association_obj = self.db_resource.session.get(
                    SearchAssociation, (value, sha)
                )
                if association_obj:
                    association_obj.weight += 1
                else:
                    association_obj = SearchAssociation(
                        term=term_obj,
                        gif=gif_obj
                    )
                    self.db_resource.session.add(association_obj)
        self.db_resource.session.commit()
        if manifest_path:
            with open(manifest_path, "w") as mp:
                json.dump(manifest, mp)

if __name__ == "__main__":
    thread = start_server()
    with open("test-gif-set.txt") as searchfile:
        fetcher = GifCitiesFetcher(searchfile)
        flaskapp.app_context().push()
        builder = DatabaseBuilder(
            fetcher, db
        )
        builder.build(
            verbose=True, manifest_path="gif_manifest.json"
        )
    stop_server(thread)
