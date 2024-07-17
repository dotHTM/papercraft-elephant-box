#!/usr/bin/env bash
# prototyping.sh

source venv/bin/activate

X=2.75
Y=3.75
Z=1.5


compactfivepanelfingerbox \
    \
    -x $X \
    -y $Y \
    -z $Z \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/compact_fingerbox

compactfivepanelfingerbox \
    \
    -x $X \
    -y $Z \
    -z $Y \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/compact_fingerbox_top

compactfivepanelfingerbox \
    \
    -x $Y \
    -y $X \
    -z $Z \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/compact_fingerbox_turn

fivepanelfingerbox \
    \
    -x $X \
    -y $Y \
    -z $Z \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/fingerbox

fivepanelfingerbox \
    \
    -x $Y \
    -y $X \
    -z $Z \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/fingerbox_turn

fivepanelfingerbox \
    \
    -x $X \
    -y $Z \
    -z $Y \
    -s 0.1 \
    \
    --dash-length 0.67 \
    --dash-period 1.5 \
    \
    --draw-laser-bed \
    -o proto/finger_top


watchbox \
    --lock-radius      0.5 \
    --lock-tab-angle   0 \
    --lock-gap-cut     0.06 \
    --lock-offset-y    0.25 \
    --lock-offset-x    0.15 \
    --lock-fold-height 0 \
    --lock-opposite \
    \
    -x $X \
    -y $Y \
    -z $Z \
    -s 0.1 \
    -c 0.25 \
    \
    --dash-length 0.02 \
    --dash-period 0.4 \
    \
    --whole-rotate 45 \
    --draw-laser-bed \
    -o proto/watchbox


elephantbox \
    --ear-flap 1 \
    --nose-width 1 \
    --back-support 0.5 \
    --side-support 0.5 \
    \
    -x $X \
    -y $Y \
    -z $Z \
    -s 0.1 \
    -c 0.25 \
    \
    --dash-length 0.02 \
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
