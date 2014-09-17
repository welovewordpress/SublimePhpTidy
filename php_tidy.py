import sublime
import sublime_plugin
import re
import os
import subprocess

class PhpTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        FILE = self.view.file_name()
        settings = sublime.load_settings('PhpTidy.sublime-settings')

        supported_filetypes = settings.get('filetypes') or ['.php', '.module', '.inc']

        print('PhpTidy: invoked on file: %s' % (FILE))

        if os.path.splitext(FILE)[1] in supported_filetypes:

            print('PhpTidy: Ok, this seems to be PHP')

            # set tidy type
            tidy_type = settings.get('tidytype') or 'wp'

            if tidy_type == 'wp':
                tidy_file = 'wp-phptidy.php'
            else:
                tidy_file = 'phptidy.php'

            # path to plugin - <sublime dir>/Packages/PhpTidy
            pluginpath = sublime.packages_path() + '/PhpTidy'
            scriptpath = pluginpath + '/' + tidy_file

            # path to temp file
            tmpfile = '/tmp/phptidy-sublime-buffer.php'
            phppath = '/usr/bin/php'

            # set different paths for php and temp file on windows
            if sublime.platform() == 'windows':
                tmpfile = pluginpath + '/phptidy-sublime-buffer.php'
                phppath = 'php.exe'

                # hide shell window in windows
                cmd = '%s -v' % ( phppath )
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                stdout, stderr = p.communicate()
                if len(stderr) != 0:
                    sublime.error_message('PhpTidy cannot find php.exe. Make sure it is available in your PATH.')


            # set script and check if it exists
            if not os.path.exists( scriptpath ):
                sublime.error_message('PhpTidy cannot find the script at %s.' % (scriptpath))
                return

            # get current buffer
            bufferLength  = sublime.Region(0, self.view.size())
            bufferContent = self.view.substr(bufferLength).encode('utf-8')

            # write tmpfile
            fileHandle = open ( tmpfile, 'wb' )
            fileHandle.write ( bufferContent )
            fileHandle.close()
            print('PhpTidy: buffer written to tmpfile: %s' % (tmpfile))


            # call phptidy on tmpfile
            scriptpath = pluginpath + '/' + tidy_file
            print('PhpTidy: calling script: %s "%s" replace "%s"' % ( phppath, scriptpath, tmpfile ) )

            # hide shell window in windows
            cmd = '%s "%s" replace "%s"' % ( phppath, scriptpath, tmpfile )
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            stdout, stderr = p.communicate()
            if len(stderr) != 0:
                sublime.error_message('There was an error calling the script' )

            # read tmpfile and delete
            fileHandle = open ( tmpfile, 'r' )
            newContent = fileHandle.read()
            fileHandle.close()
            os.remove( tmpfile )
            print('PhpTidy: tmpfile was processed and removed')

            # remove hidden tmp file generated by phptidy.php
            if os.path.exists('/tmp/.phptidy-sublime-buffer.php.phptidybak~'):
                os.remove( '/tmp/.phptidy-sublime-buffer.php.phptidybak~' )

            # write new content back to buffer
            self.view.replace(edit, bufferLength, self.fixup(newContent))


            # reminder: different ways of logging errors in sublime
            #
            # sublime.status_message('opening file: %s' % (FILE))
            # sublime.error_message(tmpfile)
            # self.show_error_panel(self.fixup(tmpfile))


    # Error panel & fixup from external command
    # https://github.com/technocoreai/SublimeExternalCommand
    def show_error_panel(self, stderr):
        panel = self.view.window().get_output_panel("php_tidy_errors")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.erase(edit, sublime.Region(0, panel.size()))
        panel.insert(edit, panel.size(), stderr)
        panel.set_read_only(True)
        self.view.window().run_command("show_panel", {"panel": "output.php_tidy_errors"})
        panel.end_edit(edit)

    def fixup(self, string):
        return re.sub(r'\r\n|\r', '\n', string)
