import os
import pickle
import time

import serial

from image import Image
from animation import Animation
from audio import Audio

DATA_FILE = "media.dat"

# Flags the Arduino sketch expects before each payload
IMAGE_FLAG = 1
ANIMATION_FLAG = 2
AUDIO_FLAG = 3


def grid_to_hexLine(grid):
    bits = [b for row in grid for b in row]
    value = int("".join(str(int(b)) for b in bits), 2)
    pieces = [(value >> shift) & 0xFFFFFFFF for shift in (64, 32, 0)]
    return ",".join(f"0x{line:08X}" for line in pieces) + "\n"


def nextId(mediaLibrary):
    return max((m.id for m in mediaLibrary.values()), default=0) + 1


def readHeader(lines):
    """Read the 'type:', 'name:' and 'artist:' lines at the top of a media file."""
    header = {}
    for line in lines[:3]:
        key, _, value = line.partition(":")
        header[key.strip().lower()] = value.strip()
    return header["type"], header["name"], header["artist"]


def parseRow(line):
    return [int(v) for v in line.split(",")]


def readFrames(bodyLines):
    """Split an animation body into separate frames (blank lines separate them)."""
    frames, frame = [], []
    for line in bodyLines:
        if line:
            frame.append(parseRow(line))
        elif frame:
            frames.append(frame)
            frame = []
    if frame:
        frames.append(frame)
    return frames


def readNotes(bodyLines):
    """Read 'pitch,duration' lines into (pitch, duration) pairs, keeping the file's order."""
    notes = []
    for line in bodyLines:
        if line:
            pitch, duration = line.split(",")
            notes.append((int(pitch), int(duration)))
    return notes


def loadMedia(mediaLibrary):
    filename = input("Enter the name of the media file to load: ").strip()
    while not os.path.isfile(filename):
        filename = input("That file does not exist. Enter a valid file name: ").strip()

    with open(filename, "r") as f:
        lines = [line.strip() for line in f]

    mediaType, name, artist = readHeader(lines)
    body = lines[3:]

    if name in mediaLibrary:
        print(f"'{name}' is already loaded; not adding it again.")
        return

    try:
        if mediaType == "Image":
            grid = [parseRow(line) for line in body if line]
            media = Image(nextId(mediaLibrary), name, artist, grid)
        elif mediaType == "Animation":
            frames = readFrames(body)
            media = Animation(nextId(mediaLibrary), name, artist, frames)
        elif mediaType == "Audio":
            notes = readNotes(body)
            media = Audio(nextId(mediaLibrary), name, artist, notes)
        else:
            print(f"Sorry, '{mediaType}' media is not supported yet.")
            return
    except ValueError as error:
        print(f"Could not load '{filename}': {error}")
        return

    mediaLibrary[name] = media
    print(f"Loaded {mediaType} '{name}' by {artist}.")


def displayMedia(mediaLibrary, arduino):
    if not mediaLibrary:
        print("There is no media yet. Please load some media first!")
        return

    by_id = {m.id: m for m in mediaLibrary.values()}
    for m in sorted(by_id.values(), key=lambda m: m.id):
        print(f"\nID: {m.id}  Name: {m.name}  ({type(m).__name__})")
        print(f"Artist: {m.artist}")
        print(f"Times displayed: {m.count}")
        print(m)

    while True:
        choice = input("\nEnter the ID of the media to display: ").strip()
        if choice.isdigit() and int(choice) in by_id:
            break
        print("Sorry, that is not a valid media ID. Please try again.")

    media = by_id[int(choice)]

    if isinstance(media, Image):
        arduino.write(f"{IMAGE_FLAG}\n".encode())
        arduino.write(grid_to_hexLine(media.grid).encode())
    elif isinstance(media, Animation):
        arduino.write(f"{ANIMATION_FLAG}\n".encode())
        arduino.write(f"{media.numFrames()}\n".encode())
        for frame in media.frames:
            arduino.write(grid_to_hexLine(frame).encode())
    elif isinstance(media, Audio):
        arduino.write(f"{AUDIO_FLAG}\n".encode())
        for pitch, duration in media.notes:
            arduino.write(f"{pitch},{duration}\n".encode())
    else:
        print(f"Sorry, {type(media).__name__} media can't be displayed yet.")
        return

    media.incrementCount()


def main():
    # MacOS
    arduino = serial.Serial(port='/dev/cu.usbmodem3CDC75F145B02', baudrate=9600, timeout=.1)

    # Linux
    # arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)

    # Windows
    # arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
    time.sleep(2)

    mediaLibrary = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            mediaLibrary = pickle.load(f)

    print("Welcome to the Arduino LED Matrix Media Manager!")
    while True:
        print("\n1) Load media\n2) Display media\n3) Quit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            loadMedia(mediaLibrary)
        elif choice == "2":
            displayMedia(mediaLibrary, arduino)
        elif choice == "3":
            with open(DATA_FILE, "wb") as f:
                pickle.dump(mediaLibrary, f)
            arduino.close()
            print("Goodbye!")
            break
        else:
            print("That is not a valid option. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
