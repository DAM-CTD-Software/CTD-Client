#!/bin/bash

# Define paths
PYPROJECT_PATH="pyproject.toml"
OUTPUT_RC_PATH="version.txt"

# if argument given, use that as version string
if [[ $# -gt 0 ]]; then
    export VERSION="$1"
# otherwise, get the latest git tag
else
    VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
fi

VERSION="${VERSION:1}"

# Extract project metadata from pyproject.toml using tomlq and jq
NAME=$(tomlq -r '.project.name // "CTD-Client"' "$PYPROJECT_PATH")
DESCRIPTION=$(tomlq -r '.project.description // ""' "$PYPROJECT_PATH")
AUTHOR_NAME=$(tomlq -r '.project.authors[0].name // "Emil Michels"' "$PYPROJECT_PATH")

# Define static values
COPYRIGHT_YEAR="2024-2025"
COPYRIGHT_TEXT="Copyright $COPYRIGHT_YEAR $AUTHOR_NAME"
COMPANY_NAME="German Alliance for Marine Research (DAM); Leibniz Institute for Baltic Sea Research Warnemünde (IOW)"

# Split version into parts (e.g., "1.2.3" -> "1, 2, 3, 0")
IFS='.' read -ra VERSION_PARTS <<<"$VERSION"
while [ ${#VERSION_PARTS[@]} -lt 4 ]; do
    VERSION_PARTS+=("0")
done
VERSION_TUPLE="(${VERSION_PARTS[0]}, ${VERSION_PARTS[1]}, ${VERSION_PARTS[2]}, ${VERSION_PARTS[3]})"

# Generate the output file
cat >"$OUTPUT_RC_PATH" <<EOF
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=$VERSION_TUPLE,
    prodvers=$VERSION_TUPLE,
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct('CompanyName', '$COMPANY_NAME'),
        StringStruct('FileDescription', '$DESCRIPTION'),
        StringStruct('FileVersion', '$VERSION'),
        StringStruct('InternalName', '$NAME'),
        StringStruct('LegalCopyright', '$COPYRIGHT_TEXT'),
        StringStruct('OriginalFilename', 'ctdclient.exe'),
        StringStruct('ProductName', '$NAME'),
        StringStruct('ProductVersion', '$VERSION')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
EOF

echo "Generated $OUTPUT_RC_PATH"
