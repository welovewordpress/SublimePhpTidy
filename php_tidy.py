import sublime, sublime_plugin, re

class PhpTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        FILE = self.view.file_name()
        if FILE[-3:] == 'php':

            # path to temp file
            tmpfile = '/tmp/phptidy-sublime-buffer.tmp'

            # get current buffer
            bufferLength  = sublime.Region(0, self.view.size())
            bufferContent = self.view.substr(bufferLength).encode('utf-8')

            # write tmpfile
            fileHandle = open ( tmpfile, 'w' ) 
            fileHandle.write ( bufferContent ) 
            fileHandle.close() 

            # call phptidy on tmpfile
            os.system( "./wp-phptidy.php replace " + tmpfile )

            # read tmpfile and delete
            fileHandle = open ( tmpfile, 'r' ) 
            newContent = fileHandle.read() 
            fileHandle.close() 
            os.remove( tmpfile )

            # write new content back to buffer
            self.view.replace(edit, bufferLength, self.fixup(newContent))

    def fixup(self, string):
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))
