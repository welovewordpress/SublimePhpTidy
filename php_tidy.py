import sublime, sublime_plugin, re, os

class PhpTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        FILE = self.view.file_name()

        print('PhpTidy: invoked on file: %s' % (FILE))

        if FILE[-3:] == 'php':

            # path to temp file
            tmpfile = '/tmp/phptidy-sublime-buffer.php'

            # path to plugin - <sublime dir>/Packages/SublimePhpTidy
            pluginpath = os.path.abspath(os.path.dirname(__file__))
            # print 'PhpTidy: running from %s' % pluginpath
            print('PhpTidy: file seems to be PHP')            

            # get current buffer
            bufferLength  = sublime.Region(0, self.view.size())
            bufferContent = self.view.substr(bufferLength).encode('utf-8')

            # write tmpfile
            fileHandle = open ( tmpfile, 'w' ) 
            fileHandle.write ( bufferContent ) 
            fileHandle.close() 
            print('PhpTidy: tmpfile written: %s' % (tmpfile))


            # call phptidy on tmpfile
            scriptpath = pluginpath + '/wp-phptidy.php'
            print('PhpTidy: calling script: "%s" replace "%s"' % ( scriptpath, tmpfile ) )
            retval = os.system( '"%s" replace "%s"' % ( scriptpath, tmpfile ) )
            cwd = os.getcwd()
            if retval != 0:
                print('PhpTidy: script returned: %s' % (retval))
                if retval == 32512:
                    sublime.error_message('PhpTidy cannot find the script at %s.' % (scriptpath))
                else:
                    sublime.error_message('There was an error calling the script at %s. Return value: %s' % (scriptpath,retval))


            # read tmpfile and delete
            fileHandle = open ( tmpfile, 'r' ) 
            newContent = fileHandle.read() 
            fileHandle.close() 
            os.remove( tmpfile )
            os.remove( '/tmp/.phptidy-sublime-buffer.php.phptidybak~' )
            print('PhpTidy: tmpfile was processed and removed')

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
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))
