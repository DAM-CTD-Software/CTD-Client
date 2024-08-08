#!.venv/Scripts/python
from pathlib import Path
import sys
import importlib.metadata
import argparse
import subprocess
import shutil
import PyInstaller.__main__
from tufup.repo import Repository

def main(target_dir: Path, release: bool, test: bool):
    print('\nRunning \"poetry install\" to ensure latest versions and bump version number.', flush=True)
    ps = subprocess.Popen(['poetry', 'install', '--without', 'dev'])
    ps.wait()

    print('\nRunning PyInstaller to create a new bundled executable.', flush=True)
    PyInstaller.__main__.run([
        '-y',
        'windows.spec',
        f'--distpath {target_dir}',
    ])

    if not target_dir.exists():
        target_dir.mkdir()
    shutil.copyfile("dist/ctdclient.exe", target_dir.joinpath("ctdclient.exe"))

    if release:
        # find the bundled ctdclient.exe and its files
        print('\nRunning tufup to create a new release.', flush=True)
        # target_dir = Path(target_dir)
        if target_dir.exists():
            repo = Repository.from_config()
            repo.add_bundle(
                new_bundle_dir=target_dir,
                new_version= importlib.metadata.version("ctdclient"),
                custom_metadata={'changes': ''},
                skip_patch=True)
            print('\nPublish tufup changes.', flush=True)
            repo.publish_changes(private_key_dirs=['tufup_keys'])
        
    if not test:
        # push updates on webserver
        print('\nRsync with webserver space.', flush=True)
        ps = subprocess.Popen(['rsync', '-a', 'updates/', '/v/Projekte/DAM_Underway/ctdclient/updates/'])
        ps.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--target_dir',
        '-d',
        type=str,
        default='dist/ctdclient',
        help="The target dir for the final exe, usually dist/ctdclient"
    )
    parser.add_argument(
        '--release',
        '-r',
        action="store_true",
        default=False,
        help="Whether to use tufup to publish a new release target. DEFAULT=False"
        )
    parser.add_argument(
        '--test',
        '-t',
        action="store_true",
        default=False,
        help="Whether to not rsync with the server space on netapp1/mt. DEFAULT=False"
        )
    args = parser.parse_args()
    main(Path(args.target_dir), args.release, args.test)
    sys.exit(0)