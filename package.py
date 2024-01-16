from setuptools import Command

import shlex
import subprocess
import os
import sys

PACKAGES = "packages"

class BundlePackage(Command):
    """ Package python script and dependencies """
    description = "Bundle packages and depedancies offline"
    user_options = []

    def __init__(self, dist):
        Command.__init__(self, dist)

    def initialize_options(self):
        """ To be implemented """
        pass

    def finalize_options(self):
        """ To be implemented """
        pass

    def recreate_requirements(self):
        """ Recreate requirements.txt in simple format like
            pkg1_name op version
            original requirement.txt may contain URLs. for local
            installation we do not need them

            Also, retain original requirements.txt as requirements.org
        """
        if not os.path.exists("requirements.txt"):
            print "Not found requirements.txt file"
            sys.exit(1)

        requirements = open("requirements.txt").read().split("\n")
        local_requirements = []

        for requirement in requirements:
            if requirement:
                if "egg=" in requirement:
                    pkg_name = requirement.split("egg=")[-1]
                    local_requirements.append(pkg_name)
                elif "git+" in requirement:
                    pkg_name = requirement.split("/")[-1].split(".")[0]
                    local_requirements.append(pkg_name)
                else:
                    local_requirements.append(requirement)

        print "Packages in wheel: %s", local_requirements
        self.execute("mv requirements.txt requirements.org")

        with open("requirements.txt", "w") as requirements_file:
            requirements_file.write("\n".join(filter(None, local_requirements)))

    def execute(self, command, capture_output=False):
        """ Execute a command and update STDOUT """

        print "Running shell command: %s" % command

        if capture_output:
            return subprocess.check_output(shlex.split(command))

        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print output.strip()

        return_code = process.poll()

        if return_code != 0:
            print "Error running command %s - exit code: %s", command, return_code
            raise IOError("Shell Commmand Failed")

        return return_code

    def run_commands(self, commands):
        for command in commands:
            self.execute(command)

    def restore_requirements_txt(self):
        if os.path.exists("requirements.org"):
            print "Restoring original requirements.txt file"
            commands = [
                "rm requirements.txt",
                "mv requirements.org requirements.txt"
            ]
            self.run_commands(commands)

    def run(self):
        commands = []
        commands.extend([
            "rm -rf {dir}".format(dir=PACKAGES),
            "mkdir -p {dir}".format(dir=PACKAGES),
            "pip --no-python-version-warning wheel --wheel-dir={dir} -r requirements.txt".format(dir=PACKAGES)
        ])

        print "Download requirements.txt into packages folder"
        self.run_commands(commands)
        print "Generating local requirements.txt"
        self.recreate_requirements()

        print "Packaging python scripts and packages into dist"
        self.run_command("sdist")
        self.restore_requirements_txt()
