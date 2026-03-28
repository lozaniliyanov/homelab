#!/bin/bash
# Wrapper to give claude a pseudo-TTY so it runs in interactive/channels mode
# without a real terminal attached.
exec script -q -f -c "/home/lozaniliyanov/.local/bin/claude --channels plugin:telegram@claude-plugins-official" /dev/null
