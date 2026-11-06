#!/usr/bin/env bash
# Copy the SDLC skills into a project repository for Claude Code and/or Kiro.
#
# Usage: ./install.sh <target-repo> [claude|kiro|both]   (default: both)
#
# Skills are copied (not symlinked) so they are committed with the project and the
# whole team gets the same version. Re-run to update; existing sdlc-* folders are replaced.
set -euo pipefail

target="${1:-}"
tool="${2:-both}"
if [[ -z "$target" || ! -d "$target" ]]; then
  echo "Usage: $0 <target-repo> [claude|kiro|both]" >&2
  exit 2
fi
case "$tool" in
  claude) dests=(".claude/skills") ;;
  kiro)   dests=(".kiro/skills") ;;
  both)   dests=(".claude/skills" ".kiro/skills") ;;
  *) echo "Second argument must be claude, kiro or both" >&2; exit 2 ;;
esac

src="$(cd "$(dirname "$0")" && pwd)/skills"
for dest in "${dests[@]}"; do
  mkdir -p "$target/$dest"
  for skill in "$src"/sdlc-*/; do
    name="$(basename "$skill")"
    rm -rf "${target:?}/$dest/$name"
    cp -R "$skill" "$target/$dest/$name"
    echo "installed $dest/$name"
  done
done
echo "Done. Commit the copied folders in $target so the team shares them."
