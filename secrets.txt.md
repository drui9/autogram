## `unlock sublime-text-4`
This guide also works for linux. The file that needs to be replaced is located in: 
```/opt/sublime_text/sublime_text``` in case of debian based systems. (Ubuntu, Debian etc.)

- Go to https://hexed.it/
- Click Open File in the top left corner and select /opt/sublime_text/sublime_text
- Press CTRL + F or on the Search for bar in the left panel and look for: 80 78 05 00 0f 94 C1
- Now in the editor, click on the first byte (80) and start replacing each byte by: C6 40 05 01 48 85 C9
- Finally, in the top left corner again, click on Export Button. This will download the file in your Downloads Folder.
- Execute sudo cp ~/Downloads/sublime_text /opt/sublime_text/sublime_text to replace the original file.
