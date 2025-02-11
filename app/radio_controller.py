"""
Multithreaded object managing Icecast broadcast, crossfading, and
    Song loading. "startup" and "shutdown" should be called by the
    server at startup and shutdown.
"""
import logging
import signal
import time
import os
import uuid
import sys
import random
import shout
import threading
import queue
from io import BytesIO
from pydub import AudioSegment
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app import flaskapp, db, appconfig, constants
from app.models import Song

class RadioController():
    """
    Object encapsulating radio control functions.
    """
    def __init__(self): 
        """
        Initialization actions. Create Shout object with parameters
            from appconfig.
        """
        self.stream_obj = shout.Shout()

        # I could do some eldritch "exec()" calls here to set all
        # these, but that's too much to avoid a dozen lines of 
        # longhand. this is a good library, but boo to the dev
        # for not providing a way to pass all these settings
        # as a dict or something

        self.stream_obj.host = appconfig["ICECAST_HOST"]
        self.stream_obj.port = appconfig["ICECAST_PORT"]
        self.stream_obj.mount = appconfig["ICECAST_MOUNTPOINT"]
        self.stream_obj.user = appconfig["ICECAST_USERNAME"]
        self.stream_obj.password = appconfig["ICECAST_PASSWORD"]
        self.stream_obj.format = appconfig["ICECAST_FORMAT"]
        self.stream_obj.protocol = appconfig["ICECAST_PROTOCOL"]
        self.stream_obj.name = appconfig["ICECAST_NAME"]
        self.stream_obj.genre = appconfig["ICECAST_GENRE"]
        self.stream_obj.url = appconfig["ICECAST_URL"]
        self.stream_obj.audioinfo = {
            shout.SHOUT_AI_BITRATE: str(appconfig["ICECAST_BITRATE"]),
            shout.SHOUT_AI_SAMPLERATE: str(
                appconfig["ICECAST_SAMPLERATE"]),
            shout.SHOUT_AI_CHANNELS: str(appconfig["ICECAST_CHANNELS"])
        }

        self.stream_thread = None
        self.gen_songs_thread = None

        self.segment_queue = queue.Queue()

        # "gen_songs" will respond to skip_signal, clearing
        # the queue and generating an uncrossfaded next track
        # featuring the "skip" sound byte. It'll then set the 
        # stream_skip_subsignal to signal the "stream" thread
        # to skip to the next song on the queue
        self.skip_signal = threading.Event()
        self.stream_skip_subsignal = threading.Event()
        self.kill_signal = threading.Event()

    def startup(self):
        """
        Startup actions. Connects shout object and starts stream 
            thread.
        """
        flaskapp.logger.info("Starting radio controller thread")
        stream_opened = False
        stream_connected = False
        self.gen_songs_thread = self.stream_thread = self.monitor_skip_thread = None
        tries = 0
        while not stream_connected:
            try:
                if not stream_opened:
                    err_code = self.stream_obj.open() 
                    flaskapp.logger.info(f"open resp: {err_code}")
                    # This method actually returns 1 on success
                    stream_opened = (
                        err_code == 1
                    )
                if stream_opened:
                    err_code = self.stream_obj.get_connected()
                    flaskapp.logger.info(f"connect resp: {err_code}")
                    stream_connected = (
                        err_code == shout.SHOUTERR_CONNECTED
                    )
            except Exception as e:
                err_code = f"{type(e).__name__}: {str(e)}"
            if not stream_connected:
                tries += 1
                if tries >= 3:
                    flaskapp.logger.error(
                        "Unable to start Shout stream.\nOpened: " +
                        f"{'true' if stream_opened else 'false'}" +
                        "\nConnected: " + 
                        f"{'true' if stream_connected else 'false'}" +
                        f"\nError Code: {err_code}"
                    )
                    return
                time.sleep(0.5)

        self.gen_songs_thread = threading.Thread(
            target=self.gen_songs
        )
        self.gen_songs_thread.start()

        self.stream_thread = threading.Thread(
            target=self.stream
        )
        self.stream_thread.start()

        self.monitor_skip_thread = threading.Thread(
            target=self.monitor_skip
        )
        self.monitor_skip_thread.start()

    def shutdown(self):
        """
        Shutdown actions. Stops running threads.
        """
        self.kill_signal.set()
        if self.gen_songs_thread:
            self.gen_songs_thread.join()
        if self.stream_thread:
            self.stream_thread.join()
        if self.monitor_skip_thread:
            self.monitor_skip_thread.join()
        
        try:
            self.stream_obj.close()
        except shout.ShoutException:
            pass

    def skip_song(self):
        """
        Convenience method to skip song. Sets "skip_signal" Event
            object.
        """
        self.skip_signal.set()

    def get_next_song_file(self):
        """
        Helper method for "gen_songs", queries database for oldest
            queued Song and returns its local filename. If no songs 
            are queued, returns a random song from the songs dir.
        :return: name of file in songs directory
        """
        with flaskapp.app_context(), Session(db.engine) as session:
            try:
                queued_song = session.scalars(
                    db.select(Song).filter_by(
                        status=constants.QUEUED_SONG
                    ).order_by(
                        Song.status_updated_time.asc()
                    )
                ).first()
            except OperationalError:
                queued_song = None
        if queued_song:
            return queued_song.uri
        else:
            otto_uri = random.choice(
                os.listdir(appconfig["SONG_PATH"]))
            song_added = False
            tries = 0
            while not song_added:
                with flaskapp.app_context():
                    try:
                        otto_song = Song(
                            song_id=uuid.uuid1().hex,
                            uri=otto_uri
                        )
                        session.add(otto_song)
                        session.commit()
                        song_added = True
                    except IntegrityError:
                        tries += 1
                        if tries >= 3:
                            flaskapp.logger.error(
                                f"Unable to add autoplay song after " +
                                "too many uuid conflicts. This is " +
                                "statistically impossible. If you're " +
                                "reading this, go buy a lottery ticket."
                           )
            return otto_uri

    def iterate_playing_song(self):
        """
        Helper method for "gen_songs", change the status of any songs
            marked "playing" to "played", then change the oldest 
            queued song status to "playing"
        """
        try:
            with flaskapp.app_context(), Session(db.engine) as session:
                playing_songs = session.scalars(
                    db.select(Song).filter_by(
                        status=constants.PLAYING_SONG
                    )
                ).all()
                for song in playing_songs:
                    song.status = constants.PLAYED_SONG
                next_song = session.scalars(
                    db.select(Song).filter_by(
                        status=constants.QUEUED_SONG
                    ).order_by(
                        Song.status_updated_time.asc()
                    )
                ).first()
                if next_song:
                    next_song.status = constants.PLAYING_SONG
                session.commit()
        except OperationalError as e:
            flaskapp.logger.error(f"OperationalError in " +
                f"iterate_playing_song: {str(e)}")

    def gen_songs(self):
        """
        Thread which monitors the segment queue and generates the next
            song when it's empty. In practice, this means that there
            will be a one-song buffer between the current song and
            any newly queued one. Chops off last CROSSFADE_LENGTH * 2
            seconds of the song to be crossfaded with the next one.
        """
        try:
            # split the current track a bit from the end and save
            # the last bit, to crossfade with the next track
            curr_song_file = ""
            curr_song_end = None

            # append new segment files to this, and always
            # delete all files except the last two (i.e. the 
            # one currently being played by "stream" and the one that
            # was just created
            segment_files = []

            # preload "skip" sound effect
            skip_segment = AudioSegment.from_file(
                appconfig["SKIP_MP3_PATH"],
                format="mp3",
                sample_width=appconfig["ICECAST_BITRATE"] // 64,
                frame_rate=appconfig["ICECAST_SAMPLERATE"],
                channels=appconfig["ICECAST_CHANNELS"]
            )

            while not self.kill_signal.is_set():
                # queue is empty, generate the next track
                if self.segment_queue.empty():
                    # Sleep until the crossfade begins, then iterate
                    # playing song. I could break that off into a
                    # separate thread, but I don't really want
                    # to increase the complexity more than I have to,
                    # plus it's good to give more CPU time
                    # to the other thread when it's switching

                    # if curr_song_end is None, indicates a skip
                    # so no sleep
                    if curr_song_end:
                        time.sleep(appconfig["CROSSFADE_LENGTH"] / 1000)

                    next_song_file = self.get_next_song_file()
                    self.iterate_playing_song()
                    flaskapp.logger.info(f"Generating segment for " +
                                        f"{next_song_file}...")
                    self.stream_obj.set_metadata({
                        "song": os.path.splitext(
                            curr_song_file
                        )[0]
                    })
                    next_song = AudioSegment.from_file(
                        os.path.join(
                            appconfig["SONG_PATH"],
                            next_song_file
                        ),
                        format="mp3",
                        # 1 - 64-bit, 2 - 128-byte, etc...
                        sample_width=appconfig["ICECAST_BITRATE"] // 64,
                        frame_rate=appconfig["ICECAST_SAMPLERATE"],
                        channels=appconfig["ICECAST_CHANNELS"]
                    )
                    next_song_start = next_song[
                        :-2 * appconfig["CROSSFADE_LENGTH"]]
                    next_song_end = next_song[
                        -2 * appconfig["CROSSFADE_LENGTH"]:]

                    segment_file = None
                    while (not segment_file or 
                            os.path.exists(segment_file)):
                        segment_file = os.path.join(
                            appconfig["TMP_PATH"], uuid.uuid1().hex
                        )
                    if curr_song_end:
                        curr_song_end.append(
                            next_song_start,
                            crossfade=appconfig["CROSSFADE_LENGTH"]
                        ).export(segment_file, format="mp3")
                    # if curr_song_end is none, a Skip signal has been
                    # recieved (or it's just starting, and imo the skip
                    # sound effect can play then too)
                    else:
                        skip_segment.append(next_song_start).export(
                            segment_file, format="mp3")
                    self.segment_queue.put(segment_file)
                    
                    segment_files.append(segment_file)
                    for played_file in segment_files[:-2]:
                        try:
                            os.remove(played_file)
                        except FileNotFoundError:
                            pass
                    segment_files = segment_files[-2:]

                    curr_song_end = next_song_end
                    curr_song_file = next_song_file

                # on skip, clear the queue and signal the "stream" thread
                # to skip its current segment
                if self.skip_signal.is_set():
                    curr_song_end = None
                    while not self.segment_queue.empty():
                        try:
                            self.segment_queue.get_nowait()
                        except queue.Empty:
                            pass
                    self.stream_skip_subsignal.set()
                    self.skip_signal.clear()

        except Exception as err:
            _, _, exc_tb = sys.exc_info()
            flaskapp.logger.error("Error in gen_songs:" + 
                "%s: %s: %s at line %d" % (
                    err.__class__.__name__, 
                    err.__class__.__name__, 
                    str(err), exc_tb.tb_lineno))

    def stream(self):
        CHUNK_SIZE = 8192

        try:
            while not self.kill_signal.is_set():
                try:
                    segment = self.segment_queue.get_nowait()
                except queue.Empty:
                    continue
                current_seg_fp = open(segment, "rb")
                byte_chunk = current_seg_fp.read(CHUNK_SIZE)
                while 1:
                    next_byte_chunk = current_seg_fp.read(CHUNK_SIZE)
                    self.stream_obj.send(byte_chunk)

                    # break out of immediate loop when receiving skip
                    if len(next_byte_chunk) == 0:
                        break

                    if self.stream_skip_subsignal.is_set():
                        self.stream_skip_subsignal.clear()
                        break

                    if self.kill_signal.is_set():
                        break

                    byte_chunk = next_byte_chunk
                    self.stream_obj.sync()
        except Exception as err:
            _, _, exc_tb = sys.exc_info()
            flaskapp.logger.error("Error in stream: " +
                "%s: %s: %s at line %d" % (
                    err.__class__.__name__, 
                    err.__class__.__name__, 
                    str(err), exc_tb.tb_lineno))

    def monitor_skip(self):
        while not self.kill_signal.is_set():
            with flaskapp.app_context(), Session(db.engine) as session:
                try:
                    playing_song = session.scalars(
                        db.select(Song).filter_by(
                            status=constants.PLAYING_SONG
                        )
                    ).first()
                    if playing_song and (
                            len(playing_song.broken_hearted_users) -
                            len(playing_song.hearted_users) >=
                            appconfig["BROKENHEARTS_TO_SKIP"]):
                        self.skip_song()
                except OperationalError:
                    pass
                time.sleep(appconfig["MONITOR_SKIP_SLEEP"])
