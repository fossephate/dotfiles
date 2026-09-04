#!/bin/bash
# Run from exec-on-workspace-change: pull the OpenPets pet onto the focused
# workspace, then snap it back to its home spot (bottom-right, tucked 110px past
# where OpenPets' on-screen confinement would leave it).
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

HOME_X=1282
HOME_Y=584

ws="${AEROSPACE_FOCUSED_WORKSPACE:-$(aerospace list-workspaces --focused)}"

ids=$(aerospace list-windows --monitor all --app-bundle-id dev.openpets.app --format '%{window-id}')
[ -z "$ids" ] && exit 0
for id in $ids; do
  aerospace move-node-to-workspace --window-id "$id" "$ws" >/dev/null 2>&1
done

# AeroSpace re-applies the frame shortly after the move, so set it a few times.
for _ in 1 2 3; do
  osascript -e "tell application \"System Events\" to tell process \"OpenPets\" to set position of window \"OpenPets Default Pet\" to {$HOME_X, $HOME_Y}" >/dev/null 2>&1
  sleep 0.25
done
