# Author: Henry McIntyre (github.com/mcintyrehh)
# Largely based on the rpi-ws281x examples (https://github.com/rpi-ws281x/rpi-ws281x-python)

import os
import time
import json
import argparse
import requests
from rpi_ws281x import *

from dotenv import load_dotenv
load_dotenv()

# Set ENV Variables
TAUTULLI_API_KEY = os.getenv('TAUTULLI_API_KEY')
TAUTULLI_IP = os.getenv('TAUTULLI_URL')

# LED strip configuration:
LED_COUNT      = 30      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 30     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
#LED_STRIP      = ws.SK6812_STRIP_RGBW
LED_STRIP      = ws.SK6812W_STRIP


# Define functions which animate LEDs in various ways.

def light_streams(strip, color, streams):
	"""Display streams in static color"""
	for i in range(strip.numPixels()):
		if(i < streams):
			strip.setPixelColor(i, color)
		else:
			strip.setPixelColor(i, Color(0,0,0))
		strip.show()

def color_wipe(strip, color, wait_ms=50):
	"""Wipe color across display one pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms / 1000.0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255-pos*3, 0, pos*3)
	else:
		pos -= 170
		return Color(0, pos*3, 255-pos*3)




def streams_rainbow(strip, streams, wait_ms=20, iterations=5):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			if(i<streams):
				strip.setPixelColor(i, wheel((i+j) & 255))
			else:
				strip.setPixelColor(i, Color(0,0,0))
		strip.show()
		time.sleep(wait_ms/1000.0)


def streams_rainbow_cycle(strip, streams, wait_ms=20, iterations=10):
        for j in range(256*iterations):
                for i in range(strip.numPixels()):
                        if(i<streams):
                                strip.setPixelColor(i, wheel((int(i*256/streams) + j) & 255))
                        else:
                                strip.setPixelColor(i, Color(0,0,0))
                strip.show()
                time.sleep(wait_ms/1000.0)

# Get stream info from Tautulli
def stream_count():
	"""Returns an int of current streams or None"""
	tautulli_url = f"{TAUTULLI_IP}/api/v2?apikey={TAUTULLI_API_KEY}&cmd=get_activity"
	try:
		res = requests.get(tautulli_url).json()
		stream_count =  res['response']['data'].get('stream_count')
		if (stream_count is not None):
			stream_count = int(stream_count)
		return stream_count

	except Exception as e:
		print(e)

# Main program logic follows:
if __name__ == '__main__':
    print('stream-lights.py init')

    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            streams = stream_count()
            #print("# of streams: ", streams)
            if(streams is not None):
            	 streams_rainbow(strip, streams)

    except KeyboardInterrupt:
        if args.clear:
            color_wipe(strip, Color(0,0,0), 10)


