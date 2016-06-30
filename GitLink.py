import os
import re
import webbrowser
import sublime
import sublime_plugin
import subprocess

class LinktogitCommand(sublime_plugin.TextCommand):

    def getoutput(self, command):
        out, err = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
        return out.decode().strip()

    def run(self, edit, **args):
        # Current file path & filename

        # only works on current open file
        path, filename = os.path.split(self.view.file_name())

        # Switch to cwd of file
        os.chdir(path + "/")

        # Find the repo
        git_config_path = self.getoutput("git remote show origin -n")

        # Determine git URL which may be either HTTPS or SSH form
        # (i.e. https://domain/user/repo or git@domain:user/repo)
        #
        # parts[0][2] will contain 'domain/user/repo' or 'domain:user/repo'
        #
        # see https://regex101.com/r/pZ3tN3/2 & https://regex101.com/r/iS5tQ4/2
        p = re.compile(r"(.+: )*([\w\d\.]+)[:|@]/?/?(.*)")
        parts = p.findall(git_config_path)
        git_config = parts[0][2]

        remote_name = 'git.brainstormforce.com'
        remote = {
                'url': 'http://git.brainstormforce.com/{0}/{1}/blob/{2}/{3}{4}',
                'line_param': '#L'
            }

        # need to get username from full url
        domain, user, repo = git_config.replace(".git", "").replace(":", "/").split("/")

        # Find top level repo in current dir structure
        remote_path = self.getoutput("git rev-parse --show-prefix")

        # Find the current branch
        branch = self.getoutput("git rev-parse --abbrev-ref HEAD")

        # Build the URL
        url = remote['url'].format(user, repo, branch, remote_path, filename)


        row = self.view.rowcol(self.view.sel()[0].begin())[0] + 1
        url += "{0}{1}".format(remote['line_param'], row)

        webbrowser.open_new_tab(url)
        sublime.set_clipboard(url)
        sublime.status_message('GIT url has been copied to clipboard')