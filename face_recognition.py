import face_recognition #face recognition & detection library
import cv2 #cv2 is python lib. meant to solve computer vision problems
import RPi.GPIO as GPIO #imports gpio library for raspberry pi
import time #time allows us to handle various operations regarding time
from mcp3208 import MCP3208 
# import time
import smtplib #this is used to send the mail to any internet connected machine
from email.mime.multipart import MIMEMultipart #
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import imaplib
GPIO.setmode(GPIO.BCM)
adc = MCP3208()

rli=21 #Specifying pin number for Indoor light
oli=19 #Specifying pin number for Outdoor Light
buz=20 #Specifying pin number for Buzzer
GPIO.setup(rli, GPIO.OUT) #declaring those pins as output
GPIO.setup(oli, GPIO.OUT)
GPIO.setup(26, GPIO.OUT) #Specifying and declaring pin for relay
GPIO.setup(buz, GPIO.OUT) 
gate=13
GPIO.setup(gate, GPIO.OUT)
GPIO.output(oli, True)
GPIO.output(rli, True)
GPIO.output(26, False)
GPIO.output(buz, True)
pwm=GPIO.PWM(gate, 50) #create pwm on gate pin and set it to 50Hz
def SetAngle(angle):
	duty = angle / 18 + 2 
	GPIO.output(gate, True)
	pwm.ChangeDutyCycle(duty) #providing duty cycle in range 0-100
	time.sleep(1) #specifying sleep time of 1sec i.e 1000ms
	GPIO.output(gate, False)
	pwm.ChangeDutyCycle(0)
pwm.start(0)

def gate_open():
    SetAngle(90) #
def gate_close():
    SetAngle(0)
def buz_on():
    GPIO.output(buz, False)
def buz_off():
    GPIO.output(buz, True)
#####################mail sending
def mails(count):
    count=str(count)
    fromaddr = 'finalyrproject06@gmail.com' #sender email address(raspberry pi)
    password='cpsi yygacvba dyuw'
    toaddr = 'siddheshthipse@gmail.com'     #reciever email address

    # calling the Multipurpose Internet Mail Extension function
    msg = MIMEMultipart()
    msg['From'] = fromaddr 
    msg['To'] = toaddr 

    # storing the subject 
    msg['Subject'] = "Person"

    # string to store the body of the mail 
    body = count
    msg.attach(MIMEText(body, 'plain'))
    filename='1.jpg'
    #filename = filename
    attachment = open(filename, "rb") 

     # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment).read()) 

    # Encode file in ASCII characters to send by email 
    encoders.encode_base64(p) 

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 

    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 

    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 

    # start TLS for security 
    s.starttls() 

    # Authentication 
    s.login(fromaddr, password) 

    # Converts the Multipart msg into a string 
    text = msg.as_string() 

    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
 #####################extract features     
video_capture = cv2.VideoCapture(0)
f1_image = face_recognition.load_image_file("1.jpeg") #uploading the images of the family members of home
f1_face_encoding = face_recognition.face_encodings(f1_image)[0]
f2_image = face_recognition.load_image_file("2.jpeg") #these images would be stored in the sd card which would be acting as our database
f2_face_encoding = face_recognition.face_encodings(f2_image)[0]
f3_image = face_recognition.load_image_file("3.jpeg")
f3_face_encoding = face_recognition.face_encodings(f3_image)[0]
##f4_image = face_recognition.load_image_file("4.jpeg")
##f4_face_encoding = face_recognition.face_encodings(f4_image)[0]


known_face_encodings = [
    f1_face_encoding,  
    f2_face_encoding,
    f3_face_encoding,  
   # f4_face_encoding,
   
 
]
known_face_names = [
    "1",  #these are simply the names of the photo files for eg 1.jpg
    "2",
    "3",  
  #  "4",
    
    

face_locations = [] #declaring array(list) in python
face_encodings = []
face_names = []
process_this_frame = True #declare and set variable to true
########read sensor data
def sens():
    #time.sleep(2)
    rl=adc.read(3)/10 #db
    rl=400-rl
    print('Room light')
    print(rl)
    if(rl<100):        
    
        GPIO.output(rli, False)
    else:
        GPIO.output(rli, True)
    temp=adc.read(0)/10
    print('temperature')
    print(temp)
    if(temp>30):#threshold temperature is kept at 40 degree celsius
        GPIO.output(26, True) #turn ON the fan
    else:
        GPIO.output(26, False) #turn OFF the fan
    ol=adc.read(2)/10
    ol=400-ol
    print('cam light')
    print(ol)
    if(ol<100):        
    
        GPIO.output(oli, False)
    else:
        GPIO.output(oli, True)
############read camera and recognition
while True: #setting up an infinite while loop for continously reading the frames
    sens()
    buz_off()
    ret, frame = video_capture.read() #this function returns a bool, if frame is read correctly then true or else false

   
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    
    rgb_small_frame = small_frame[:, :, ::-1]

   
    if process_this_frame: #this variable was defined to be 'true' above
      
        face_locations = face_recognition.face_locations(rgb_small_frame) #to detect the location of the face
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations) #for encoding the face

        face_names = []
        for face_encoding in face_encodings:
            
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding) #comparing the known faces with the current face
            name = "Unknown"

          
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)
            if name == "Unknown":
               
                filename = ('1.jpg') #variable named 'filename' is declared which contains image 1.jpg
                cv2.imwrite(filename, frame) #save image to the db
                
    process_this_frame = not process_this_frame


    
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if name=='Unknown':
            buz_on()
            mails('Person detected')
        else:
            gate_open()
            time.sleep(2)
            gate_close
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

       
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)#rgb values are used to decide the color of the rectangular frame 

       
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

      
    cv2.imshow('Video', frame) #displaying the frame with name 'Video'

   
    if cv2.waitKey(1) & 0xFF == ord('q'):
        breakm

#when everything is done, release the capture
video_capture.release() #used to free the resources
cv2.destroyAllWindows() #destroys all the windows created
