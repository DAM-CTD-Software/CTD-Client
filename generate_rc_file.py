from tomlkit.toml_file import TOMLFile

pyproject = TOMLFile("pyproject.toml").read()

# Extract project metadata
project = pyproject.get("project", {})
name = project.get("name", "CTD-Client")
version = project.get("version", "0.0.0")
description = project.get("description", "")
author_name = project.get("authors", [{}])[0].get("name", "Emil Michels")

# Define static values
copyright_year = "2024-2026"
copyright_text = f"Copyright {copyright_year} {author_name}"
company_name = "German Alliance for Marine Research (DAM); Leibniz Institute for Baltic Sea Research Warnemuende (IOW)"

# Split version into parts (e.g., "1.2.3" -> "1, 2, 3, 0")
version_parts = version.split(".")
while len(version_parts) < 4:
    version_parts.append("0")
version_tuple = f"({', '.join(version_parts)})"

# Generate the output file
output = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
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
        [StringStruct('CompanyName', '{company_name}'),
        StringStruct('FileDescription', '{description}'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', '{name}'),
        StringStruct('LegalCopyright', '{copyright_text}'),
        StringStruct('OriginalFilename', 'ctdclient.exe'),
        StringStruct('ProductName', '{name}'),
        StringStruct('ProductVersion', '{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

OUTPUT_RC_PATH = "version.txt"

with open(OUTPUT_RC_PATH, "w") as f:
    f.write(output)

print(f"Generated {OUTPUT_RC_PATH}")
