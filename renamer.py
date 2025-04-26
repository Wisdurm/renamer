import re
from os import listdir, rename
from os.path import isfile, join
from PIL import Image, ImageFilter, ImageEnhance
from collections import Counter
import pytesseract
# Symbols which arent commonly present in sentences
strange_symbols = ['@', '/', '[', ']', '<', '>', '|', '.', ':', ';']
# Numbers
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# Path to images
path = input('Path to images? This script will rename all images there, without pauses.\nPath:')
files = [f for f in listdir(path) if isfile(join(path, f))]

for image in files:
    # Load img (or try)
    try:
        img = Image.open(f'{path}/{image}')
    except: # Not image (or at least compatible one)
        continue
    # Grayscale
    img = img.convert('L')
    # Median
    img = img.filter(ImageFilter.MedianFilter())
    # Contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    # Actually get text
    text = pytesseract.image_to_string(img)
    # If text to parse
    if len(text) > 2: # 3 is a good bare minimum, like for cat.webp or something
        # List of words
        words = re.split(' |\n', text)
        # Filter words which may not be relevant
        # (words which contain weird symbols, like @, might be a username)
        # (numbers also usually aren't very interesting)
        i = 0        
        try:
            while i < len(words): # Changing list while iterating, and too lazy to figure out "better" way
                # Remove strange and empty words
                for symbol in strange_symbols:
                    if symbol in words[i] or len(words[i]) < 1: 
                        words.remove(words[i])
                        i -= 1
                for number in numbers:
                    if number in words[i]:
                       words.remove(words[i])
                       i -= 1
                i += 1
        except: # This is the point at which I got lazy and gave up
            continue
        # If longer sentence, keep structure, otherwise pick out key words
        if len(words) > 8:
            words = words[:8] # First 8 words
        else:
            # Filter interesting words
            # Sort by length
            words = sorted(words, key=lambda word: len(word), reverse=True)
            # Sort by occurences
            words = sorted(words, key=Counter(words).get, reverse=False)
            # 5 most interesting words
            words = words[:5]
        
        # File format of file
        file_format = image[image.rfind('.'):]
        # Change name
        name = ' '.join(words) + file_format
        # File format friendly name
        name = ''.join( x for x in name if (x.isalnum() or x in '._- '))
        
        while isfile(f'{path}/{name}'): # Don't overwrite existing files
            name = '2' + name
        
        try:
            rename(f'{path}/{image}', f'{path}/{name}')
            print(f'Renamed {image} to {name}')
        except:
            print(f'Failed to rename {image}')