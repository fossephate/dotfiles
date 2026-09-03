#!/bin/bash
# UserPromptSubmit hook: rename the Zed terminal tab to a short summary of the prompt.
#
# Relies on a local Zed patch that treats an OSC 0/2 payload prefixed with
# "zed;tab-title=" as a tab rename request. Other terminals discard the unknown
# payload, so this is a harmless no-op outside the patched build.
#
# Runs async (see settings.json) because the Haiku call takes ~2-3s.

set -uo pipefail

MARKER="zed;tab-title="

# Hooks get no controlling TTY of their own, and the immediate parent often has
# none either, so walk up the process tree to the nearest ancestor that does.
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
[ -n "$tty_path" ] || exit 0

prompt=$(jq -r '.prompt // empty' 2>/dev/null)
[ -n "$prompt" ] || exit 0

# Slash commands and bare `!` shell escapes aren't worth a model call.
case "$prompt" in
    /*|!*) exit 0 ;;
esac

# macOS ships no `timeout`, so guard the call with a background watchdog that
# kills it if the model is slow or wedged.
summarize() {
    printf '%s' "$prompt" | claude -p --model haiku \
        "Summarize the user's session as a terminal tab label: at most 4 words, lowercase, no punctuation, no quotes, no preamble. Output ONLY the label." \
        2>/dev/null &
    local job=$!
    ( sleep 25; kill "$job" 2>/dev/null ) &
    local watchdog=$!
    wait "$job" 2>/dev/null
    kill "$watchdog" 2>/dev/null
}

summary=$(summarize | head -1 | tr -d '\r')

# Strip anything that would terminate the escape sequence early or smuggle in
# further control codes, then collapse whitespace.
summary=$(printf '%s' "$summary" | tr -d '\000-\037\177' | tr -s ' ' | sed 's/^ *//; s/ *$//')
[ -n "$summary" ] || exit 0

# Keep the label short enough to read in a narrow tab.
if [ "${#summary}" -gt 40 ]; then
    summary="${summary:0:40}"
fi

printf '\033]0;%s%s\007' "$MARKER" "$summary" > "$tty_path"
