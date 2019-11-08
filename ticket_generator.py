import requests
import qrcode 
import random 
import csv
import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

def get_column(file, word):
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for k,v in enumerate(row):
                if v.lower() == word.lower():
                    return k+1

# Get eventbrite token
token = open('token.txt', 'r').read()
event_id = "80301061637" # Extracted from event url

response = requests.get(
    "https://www.eventbriteapi.com/v3/events/%s/attendees" % event_id,
    headers = {
        "Authorization": "Bearer " + token,
    },
    verify = True,  # Verify SSL certificate
)
attendees = response.json()['attendees']

for i, attendee in enumerate(attendees): 
# for i in range(1):
	# TICKET TEMPLATE
	mod = 6 - i%6
	ticket_template = Image.open("templates/%s.png" % str(mod))

	#colour
	r, g, b = (0,0,0)
	if mod == 1 or mod == 2:
		r, g, b = (91,150,153)
	elif mod == 3 or mod == 4:
		r, g, b = (198,161,139)
	else:
		r, g, b = (126,107,132)

	# QR CODE GENERATION 
	order_id = attendee['order_id']
	checked_in = attendee['checked_in']
	name = attendee['profile']['name'].upper()
	student_id = attendee['profile']['email'][0:9]

	seq_num = "{0:0=3d}".format(i + 1)
	file_name = ("%s_%s" % (attendee['profile']['first_name'], attendee['profile']['last_name'])).upper()
	qr = qrcode.QRCode(
	    version = 2,
	    error_correction = qrcode.constants.ERROR_CORRECT_H,
	    box_size = 20, # Adjust size for output onto image
	    border = 0,
	)
	table_number = str(get_column("tables.csv", student_id))

	qr_data = "%s%s%s%s%s" % (name, student_id, seq_num, order_id, checked_in)
	qr.add_data(qr_data)
	qr.make(fit=True)
	qr_img = qr.make_image(back_color="transparent")
	qr_img = qr_img.resize((309,309))

	ticket_template.paste(qr_img, (347, 1444), mask=None)
	ticket = ImageDraw.Draw(ticket_template)

	#fonts
	id_font = ImageFont.truetype("Oswald-regular.ttf", 52)
	name_font = ImageFont.truetype("Oswald-regular.ttf", 57)
	table_font = ImageFont.truetype("Oswald-bold.ttf", 63)

	#name
	w,h = ticket.textsize(name, name_font)
	offset = name_font.getoffset(name)
	ticket.text(((1000-w)/2-3,66-offset[1]), name, (r,g,b), font=name_font)
	# print (65+(100-h)/2)
	#student id
	if name == 'Janice Au Yeung' or name == 'Erik Morales' or name == 'Franklin Zhang':
		student_id = 'GUEST'
	else:
		student_id = attendee['profile']['email'][0:9]
	w, h= ticket.textsize(student_id, id_font)
	ticket.text(((1000-w)/2,1927-h), student_id, (0,0,0), font=id_font)

	#student id
	w, h= ticket.textsize('TABLE ' + table_number, table_font)
	x = (1000-w)/2+ticket.textsize('TABLE ', table_font)[0]
	ticket.text(((1000-w)/2,1802-h+49), 'TABLE ', (0,0,0), font=table_font)
	ticket.text((x,1802-h+49), table_number, (r,g,b), font=table_font)

	if os.path.isfile("tickets/%s.png" % file_name):
		ticket_template.save("tickets/%s1.png" % file_name)
	else:
		ticket_template.save("tickets/%s.png" % file_name)

print('all done!')