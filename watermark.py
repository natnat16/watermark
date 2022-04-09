# -*- coding: utf-8 -*-
"""
Image Watermarking Desktop App

Created on Fri Jan  7 12:41:22 2022

@author: ANAT-H
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfile
from PIL import ImageTk, Image, ImageDraw, ImageFont
from math import atan, tan, cos, degrees as deg

BACKGROUND_COLOR = "#B1DDC6"
PINK = "#e2979c"
RED = "#e7305b"
TITLE_FONT = ("Ariel", 25, "bold")
FONT = ("Arial",13, "normal")
WM_COLORS = {
            'White': (220,220,220,120),
            'Black': (0,0,0,120),
            'Purple': (153,61,130,120),
            'Teal': (64,138,140,120)
            }
FILETYPES=[('Image Files', '*.jpeg'), ('Image Files', '*.png'), ('Image Files', '*.jpg'), ('Image Files', '*.bmp')]

def image_upload():
    '''
    Upload image from drive.

    '''
    global image, original_size, filetype
    
    # Open Dialog box
    image_name = askopenfilename(title = "Pick your image", filetypes=FILETYPES)
    # Reset add button text back (if needed)
    add_button.config(text="Add")
    
    if image_name:      
        # Create an Image object from an Image and downsize (if needed) it to fit app window
        image = Image.open(image_name)
        original_size = image.size
        filetype = image_name.split('.')[1]
        image.thumbnail((600, 600), resample=Image.ANTIALIAS) 
        
        # Create an ImageTk object to display on tkinter
        image_lbl = ImageTk.PhotoImage(image)
        
        # Display image
        label.config(image=image_lbl)
        label.image = image_lbl # keep a reference! so that the image will show
        label.grid(column=0, row=2, columnspan=3, padx=30, pady=30)
   

def check_length(*args):
    '''
    Sets text entry maximum length.
    '''
    global entered_text
    max_len = 25
    # If text is too long stop taking input
    if len(text.get()) <= max_len:
        entered_text = text.get() 
    else:
        text.set(entered_text)
  
    
def add_watermark():
    '''
    Adds a text watermark (wm) to image.

    '''
    global image, image_wm
    
    try: 
        # Create copy of the image, and take sizes
        image_wm = image.copy()
        img_w, img_h = image_wm.size
        angle = atan(img_h/img_w) # in radians
        
        # Watermark mask dimentions: 
        # width = image digonal length, height calculated with angle
        mask_w = int((img_w)/cos(angle))
        mask_h = int(mask_w*tan(angle))
        
        # Get text & color for watermark
        wm_text = text.get()
        color_name = color.get()
        
        if color_name in WM_COLORS.keys():
            wm_color = WM_COLORS[color_name]
        else:
            wm_color = WM_COLORS['White']
        
        # Create tranparent watermark mask
        watermark_img = Image.new('RGBA', (mask_w, mask_h), (0,0,0,0))
               
        # Verify the wm text will fit on the image diagonal
        # fsize=61  
        fsize=81
        margin=100          
        while True:            
            fsize -= 1
            # Create ImageDraw object
            font = ImageFont.truetype('arial.ttf', fsize)
            draw = ImageDraw.Draw(watermark_img)
            text_w, text_h = draw.textsize(wm_text, font)
            if text_w <= mask_w-margin:
                break  
            
        # Calculate the x,y coordinates of the text in middle of wm mask
        x = mask_w//2 - text_w//2 
        y = mask_h//2 - text_h//2 
        
        # Draw the text and place on watermark mask
        draw.text((x,y), wm_text, fill=wm_color, font=font)
        watermark_img = watermark_img.rotate(deg(angle), Image.BICUBIC)
        
        # Paste mask on image - at their center
        xc = int((img_w-mask_w)/2)
        yc = int((img_h-mask_h)/2)
        image_wm.paste(watermark_img, (xc ,yc), watermark_img)
        
        # Set add button text to update
        add_button.config(text="Update")
      
        # Display watermarked image
        image_lbl = ImageTk.PhotoImage(image_wm)
        label.config(image=image_lbl)
        label.image = image_lbl # keep a reference! so that the image will show
        label.grid(column=0, row=2, columnspan=3, padx=30, pady=30)

    # Make sure image is loaded
    except NameError:
        label.config(text="You must first upload \nan image")
        label.grid(column=0, row=2, columnspan=3, padx=110, pady=150)
        

def save_image():
    '''
    Saves watermarked image.

    '''
    global image_name
    try:    
        image_name  = asksaveasfile(mode='wb', defaultextension=f".{filetype}", title = "Save your image", filetypes=FILETYPES)
        if image_name: 
            # resize back to original size & save image
            image_wm_resized = image_wm.resize(original_size)
            image_wm_resized.save(image_name)
    # Make sure image is loaded        
    except NameError:
        label.config(text="You must first upload \nan image")  
        label.grid(column=0, row=2, columnspan=3, padx=110, pady=150)
    

## Set up window
window = tk.Tk()
window.title("Watermark App")
window.minsize(width=650, height=600)
window.config(bg=BACKGROUND_COLOR, padx=50, pady=10)

title = tk.Label(text="Add A Watermark to your photos!", fg=PINK, bg=BACKGROUND_COLOR, font=TITLE_FONT)
title.grid(column=0, row=0, columnspan=3, padx=10, pady=20)

label = tk.Label(text="Image here", fg='gray', bg=BACKGROUND_COLOR, font=TITLE_FONT)
label.grid(column=0, row=2, columnspan=3, padx=180, pady=180)


## Entry - wn text
text = tk.StringVar()
text_entry = tk.Entry(textvariable=text, width=20, font=FONT)
text.trace('w', check_length)
text_entry.grid(column=0, row=1,  sticky='ew',padx=10, pady=5)
text_entry.insert(0, 'Your text here')

## Option Menu - wm color
# list of colors
colors = WM_COLORS.keys()
# Variable to keep track of the option selected in OptionMenu
color = tk.StringVar()
# Set the default value of the variable
color.set("Select a Color")

# Create & configure the option menu 
color_menu = tk.OptionMenu(window, color, *colors)
color_menu.config(font=FONT, highlightthickness=0,) 
menu_font = window.nametowidget(color_menu.menuname)
menu_font.config(font=FONT)  # Set the dropdown menu's font
color_menu.grid(column=1, row=1, sticky='ew',padx=10, pady=5)

## Buttons
# add watermark
add_button = tk.Button(text="Add", command=add_watermark, width=10, font=FONT)
add_button.grid(column=2, row=1, sticky='w',padx=20)

# upload image
upload_button = tk.Button(text="Upload", command=image_upload, width=10, font=FONT)
upload_button.grid(column=0, row=3, sticky='ew',padx=20)

# save image
save_button = tk.Button(text="Save", command=save_image, width=10, font=FONT)
save_button.grid(column=1, row=3, sticky='ew')

# quit
quit_button = tk.Button(text="Quit", command=window.destroy, width=10, font=FONT)
quit_button.grid(column=2, row=3)


window.mainloop()
