#!/usr/bin/env python
import os
import subprocess
import sys

def main(versions_file, yaml):
    vars = {}
    entries = []
    have_arrow = False
    have_file = False
    file_done = False
    buf0 = ""
    buf1 = "\n"
    versions = subprocess.check_output(["bash", "-c", "set -a; source %s; env | grep ARROW; echo DEPENDENCIES ${DEPENDENCIES[*]}" % versions_file], text=True)
    with open(yaml) as yin, open(yaml + ".new", "w") as yout:
        for line in yin:
            if line.strip().startswith("ARROW_"):
                have_arrow = True
            elif have_arrow:
                if line.strip() == "- type: file":
                    have_file = True
                elif have_file:
                    if file_done:
                        buf1 += line
                    elif not line.strip():
                        file_done = True
                else:
                    buf0 += line
            else:
                yout.write(line)
        for line in versions.splitlines():
            if line.startswith("DEPENDENCIES"):
                items = line.split()[1:]
                for name, file, url in zip(items[::3], items[1::3], items[2::3]):
                    print("        %s: /run/build/arrow/cpp/thirdparty/%s" % (name, file), file=yout)
                    entries.append((url, vars[name.replace("URL", "BUILD_SHA256_CHECKSUM")], file))
            else:
                p = line.split('=')
                vars[p[0]] = p[1]
        yout.write(buf0)
        for url, sha256, file in entries:
            print("""      - type: file
        url: %s
        sha256: %s
        dest: cpp/thirdparty
        dest-filename: %s""" % (url, sha256, file), file=yout)
        yout.write(buf1)
    os.rename(yout.name, yin.name)

if __name__ == "__main__":
    main(sys.argv[1], os.path.join(os.path.dirname(__file__), "org.eclipse.sumo.yaml") if len(sys.argv) < 3 else sys.argv[2])
