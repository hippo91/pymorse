#!/usr/bin/env python3
"""
pimorse.py lights up a led according to morse alphabet 
"""
from functools import partial
import json
import os
import sys
import time
from typing import Mapping, Union
import RPi.GPIO as GPIO


MORSE_ALPHABET = {
  "A": "SL",
  "B": "LSSS",
  "C": "LSLS",
  "D": "LSS",
  "E": "S",
  "F": "SSLS",
  "G": "LLS",
  "H": "SSSS",
  "I": "SS",
  "J": "SLLL",
  "K": "LSL",
  "L": "SLSS",
  "M": "LL",
  "N": "LS",
  "O": "LLL",
  "P": "SLLS",
  "Q": "LLSL",
  "R": "SLS",
  "S": "SSS",
  "T": "L",
  "U": "SSL",
  "V": "SSSL",
  "W": "SLL",
  "X": "LSSL",
  "Y": "LSLL",
  "Z": "LLSS",
  "1": "SLLLL",
  "2": "SSLLL",
  "3": "SSSLL",
  "4": "SSSSL",
  "5": "SSSSS",
  "6": "LSSSS",
  "7": "LLSSS",
  "8": "LLLSS",
  "9": "LLLLS",
  "0": "LLLLL", 
}


def light_up_led(led: int, duration: float) -> None:
    GPIO.output(led, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(led, GPIO.LOW)


def read_config() -> Mapping[str, Union[int, float]]:
    try:
        with open("config.json", 'r') as fi:
            data = json.load(fi)
    except FileNotFoundError:
        data = {"GPIO_PIN_OUT": 40,
                "DOT_DURATION": 0.5}
    return data


def initialize_gpio(led: int) -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)
    GPIO.setup(led, GPIO.OUT)

    if GPIO.input(led):
        GPIO.output(led, GPIO.LOW)


def emit(space_duration: float, inter_letter_duration: float, inter_word_duration: float, message: str) -> None:
    for word in emit_word(inter_word_duration, message):
        for letter in emit_letter(inter_letter_duration, word):
            yield from emit_symbol(space_duration, letter)
                

def emit_symbol(space_duration: float, letter: str) -> None:
    morse_letter = MORSE_ALPHABET[letter]
    for symbol in morse_letter[:-1]:
        yield symbol
        time.sleep(space_duration)
    yield morse_letter[-1]


def emit_letter(inter_letter_duration: float, word: str) -> None:
    for letter in word[:-1]:
        print(f"Emitting letter : {letter}")
        yield letter
        time.sleep(inter_letter_duration)
    print(f"Emitting letter : {word[-1]}")
    yield word[-1]


def emit_word(inter_word_duration: float, message: str) -> None:
    words = message.split()
    for word in words[:-1]:
        print(f"Emitting word : {word}")
        yield word
        time.sleep(inter_word_duration)
    print(f"Emitting words : {words[-1]}")
    yield words[-1]



def main(message :str) -> None:
  conf = read_config()

  led = conf['GPIO_PIN_OUT']
  dot_duration = conf['DOT_DURATION']

  dash_duration = 3 * dot_duration
  space_duration = dot_duration
  inter_letter_duration = 3 * dot_duration
  inter_word_duration = 7 * dot_duration

  emit_dot = partial(light_up_led, led, dot_duration)
  emit_dash = partial(light_up_led, led, dash_duration)

  initialize_gpio(led)

  try:
      for symbol in emit(space_duration, inter_letter_duration, inter_word_duration, message.upper()):
          if symbol == "S":
              emit_dot()
          elif symbol == "L":
              emit_dash()
          else:
              raise ValueError("Only S or L are valid Morse symbols!")
  except KeyboardInterrupt:
      print("Goodbye!")
      GPIO.cleanup()
  except (KeyError, ValueError):
      GPIO.cleanup()
      raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
      print(f"Usage: {sys.argv[0]}  <message>" + os.linesep)
      sys.exit(1)
    message = sys.argv[1]
    main(message)
