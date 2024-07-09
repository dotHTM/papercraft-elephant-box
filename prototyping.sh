#!/usr/bin/env bash
# prototyping.sh

source venv/bin/activate

watchbox \
    -x 2.65 \
    -y 3.65 \
    -z 2.5 \
    -s 0.25 \
    -c 0.3 \
    --lock-radius      0.5 \
    --lock-tab-angle   20 \
    --lock-gap-cut     0.025 \
    --lock-fold-height 0.03 \
    --max-dash-length  0.06 \
    --dash-period .125 \
    --whole-rotate 45 \
    --draw-laser-bed \
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
    --draw-laser-bed \
    -o proto/elephantbox

osascript -e 'tell application "Safari"
    repeat with an_doc in every document
        if URL of an_doc ends with ".svg" then
            set URL of an_doc to (get URL of an_doc)
        end if
    end
end tell'
