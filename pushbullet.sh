#!/bin/bash

# Set the environment variable in your .bashrc file like so:
export PUSHBULLET_API="o.pk8dQKT3qTlIXP5t5UVkUjpUmAjt4FeX"
MSG="$1"

curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/pushes -d type=note -d title="Alert" -d body="$MSG"
# curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/pushes -d type=file -d title="Alert" -d body="$MSG" -d url="http://www.teslamotors.com/"
# curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/pushes -d type=file -d title="Alert" -d body="$MSG" -d file_name="image.jpg" -d file_type="image/jpeg" -d file_url="/1.jpg"
# curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/channels -d type=file -d tag="elonmnews" -d name="jesus" -d description="desc" -d image_url="https://cdn-icons-png.flaticon.com/512/2659/2659331.png" 
