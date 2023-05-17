export PUSHBULLET_API="o.pk8dQKT3qTlIXP5t5UVkUjpUmAjt4FeX"
MSG="$1"

curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/pushes -d type=file -d title="Alert" -d body="$MSG" -d file_name="image.jpg" -d file_type="image/jpeg" -d file_url="$MSG"
# curl -u $PUSHBULLET_API: https://api.pushbullet.com/v2/pushes -d type=file -d title="Alert" -d body="$MSG" -d file_name="image.jpg" -d file_type="image/jpeg" -d file_url="https://cdn-icons-png.flaticon.com/512/2659/2659331.png"

