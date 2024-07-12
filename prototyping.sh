#!/usr/bin/env bash
# prototyping.sh

source venv/bin/activate

watchbox \
    --lock-radius      0.5 \
    --lock-tab-angle   0 \
    --lock-gap-cut     0.06 \
    --lock-offset-y    0.25 \
    --lock-offset-x    0.15 \
    --lock-opposite \
    \
    -x 2.75 \
    -y 3.75 \
    -z 1 \
    -s 0.1 \
    -c 0.25 \
    \
    --max-dash-length  0.02 \
    --dash-period 0.4 \
    \
    --whole-rotate 45 \
    -o proto/watchbox


elephantbox \
    --ear-flap 1 \
    --nose-width 1 \
    --back-support 0.5 \
    --side-support 0.5 \
    \
    -x 2.75 \
    -y 3.75 \
    -z 1 \
    -s 0.1 \
    -c 0.25 \
    \
    --max-dash-length  0.02 \
    --dash-period 0.4 \
    \
    --draw-laser-bed \
    -o proto/elephantbox

osascript -e 'tell application "Safari"
    repeat with an_doc in every document
        if URL of an_doc ends with ".svg" then
            set URL of an_doc to (get URL of an_doc)
        end if
    end
end tell'
