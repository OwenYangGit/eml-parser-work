from flanker import mime
import json
raw_email = "./01.eml"

with open(raw_email, 'rb') as fhdl:
    raw_email = fhdl.read()

msg = mime.from_string(raw_email)
#print(msg.headers)
msg_item = msg.headers.items()
#print(msg_item)
#print(type(msg_item))
# for item in msg_item:
#     print(item)
#     print(type(item))
demo = json.dumps(msg_item)
# print(demo)
msg_parts = len(msg.parts)
msg_body = msg.body
#print(msg_parts)
for part in msg.parts:
    if(part.content_type == "text/html"):
        print(part.body)
        #list1 = part.body.split()
        #print(str(list1))
        text_file = open("output.html", "w")
        text_file.write(part.body)
        text_file.close()
