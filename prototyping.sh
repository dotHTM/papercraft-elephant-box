#!/usr/bin/env bash
# prototyping.sh

source venv/bin/activate

watchbox \
    -x 2.65 \
    -y 3.65 \
    -z 2.5 \
    -s 0.25 \
    -c 0.3 \
    --lock-radius      4 \
    --lock-tab-angle   0.7 \
    --lock-gap-cut     0.5 \
    --lock-fold-height -0.5 \
    --max-dash-length .06125 \
    --dash-period .25 \
    -o proto/watchbox


elephantbox \
    -x 2.65 \
    -y 3.65 \
    -z 1 \
    -s 0.25 \
    -c 0.3 \
    --ear-flap 1 \
    --nose-width 1 \
    --back-support 0.5 \
    --side-support 0.5 \
    --max-dash-length .06125 \
    --dash-period .25 \
    -o proto/elephantbox

osascript -e 'tell application "Safari"
    repeat with an_doc in every document
        if URL of an_doc ends with ".svg" then
            set URL of an_doc to (get URL of an_doc)
        end if
    end
end tell'
