#!/bin/bash
# Set the Zed terminal tab title to the label given as "$*".
#
# Relies on a local Zed patch that treats an OSC 0/2 payload prefixed with
# "zed;tab-title=" as a tab rename request. Other terminals discard the unknown
# payload, so this is a harmless no-op outside the patched build.
#
# Passing no arguments (or only whitespace) clears the custom title, restoring
# the process-derived one.

set -uo pipefail

MARKER="zed;tab-title="

# Callers get no controlling TTY of their own, and the immediate parent often
# has none either, so walk up the process tree to the nearest ancestor that does.
tty_path=""
pid=$PPID
for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ -n "$pid" ] && [ "$pid" != "0" ] && [ "$pid" != "1" ] || break
    candidate=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d '[:space:]')
    if [ -n "$candidate" ] && [ "$candidate" != "??" ] && [ -w "/dev/$candidate" ]; then
        tty_path="/dev/$candidate"
        break
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d '[:space:]')
done

if [ -z "$tty_path" ]; then
    echo "rename-tab: could not find a writable terminal device" >&2
    exit 1
fi

# Strip anything that would terminate the escape sequence early or smuggle in
# further control codes, then collapse whitespace.
label=$(printf '%s' "${*:-}" | tr -d '\000-\037\177' | tr -s ' ' | sed 's/^ *//; s/ *$//')

if [ "${#label}" -gt 40 ]; then
    label="${label:0:40}"
fi

printf '\033]0;%s%s\007' "$MARKER" "$label" > "$tty_path"

if [ -n "$label" ]; then
    echo "Tab title set to: $label"
else
    echo "Tab title cleared (restored to process-derived title)"
fi
