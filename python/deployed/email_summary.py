#!/usr/bin/env python3

# Bug view by Matt Butler, Harper Adams University 2022


import io
import numpy as np
import cv2

import ssl
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(bar,bar_l,bar_t,bar_h,trap,matrix):
    
    try:
        subject = "Weevil Trap Report <no reply>"
        body = "This is an email with attachments sent from your weevil trap. You can view the trap at https://mechatron.co.uk/weevils/uploads/latest.jpg"
        filename_bar = "activity.jpg"
        filename_trap = "trap.jpg"
        filename_matrix = "munching monsters.jpg"
        
        filename_bar_l = "lux.jpg"
        filename_bar_t = "temp.jpg"
        filename_bar_h = "RH.jpg"
        

        sender_email = 'weevils@mechatron.co.uk'
        receiver_email = ['mbutler@harper-adams.ac.uk', 'jroberts@harper-adams.ac.uk']

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = ', '.join(receiver_email)
        msg.attach(MIMEText(body, "plain"))
        print(msg)
        
        # activity chart
        (flag, bar) = cv2.imencode(".jpg", bar)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(bar)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_bar}",
        )

        # Add attachment to message
        msg.attach(part)
        print('OK Bar')
        
        
        # lux chart
        (flag, bar_l) = cv2.imencode(".jpg", bar_l)
        print('OK 1')

        part = MIMEBase("application", "octet-stream")
        part.set_payload(bar_l)
        print('OK 2')
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_bar_l}",
        )
        print('OK 3')

        # Add attachment to message
        msg.attach(part)
        print('OK Bar_l')
        
        
        # temperature chart
        (flag, bar_t) = cv2.imencode(".jpg", bar_t)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(bar_t)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_bar_t}",
        )

        # Add attachment to message
        msg.attach(part)
        print('OK Bar_t')
        
        # humidity chart
        (flag, bar_h) = cv2.imencode(".jpg", bar_h)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(bar_h)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_bar_h}",
        )

        # Add attachment to message
        msg.attach(part)
        print('OK Bar_h')
        
        
        
        # pic of trap
        (flag, trap) = cv2.imencode(".jpg", trap)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(trap)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_trap}",
        )

        # Add attachment to message
        msg.attach(part)
        
        # pic of matrix
        (flag, matrix) = cv2.imencode(".jpg", matrix)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(matrix)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_matrix}",
        )

        # Add attachment to message
        msg.attach(part)


        # and convert message to string
        text = msg.as_string()

        #server = smtplib.SMTP('smtp.123-reg.co.uk')
        #server.set_debuglevel(1)
        #server.login('weevils@mechatron.co.uk', 'W0bblepw@')  # user & password
        #server.sendmail(sender_email, receiver_email, text)
        #server.quit()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.123-reg.co.uk', 465, context=context) as server:
            server.login('weevils@mechatron.co.uk', 'W0bblepw@')
            server.sendmail(sender_email, receiver_email, text)
        print('successfully sent the mail.')
 
    except: 
        print('Something went wrong')

    

