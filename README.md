# logserver.py Documentation

This documentation provides information on how to use the `logserver.py` Python script to serve log files and their server-sent events streams via HTTP.

This script was developed with the collaboration of ChatGPT and is the result of a conversation that lasted 53 prompts and produced over 150 lines of dialogue. The `logserver.py` script is used to serve contents of logfiles and provide a landing page with a dynamically updated text field containing the contents of the logfile.

The documentation was generated fully by ChatGPT.

## Usage

To use the `logserver.py` script, follow these steps:

1. Clone the repository containing the script, or copy the script to your local machine.
2. Install any required dependencies (if any).
3. Set the `FILE_PATHS` and `TAIL_LENGTH` environment variables to specify the file paths and tail lengths for the log files you want to serve.
4. Run the script using the command `python logserver.py`.
5. Access the log files and their respective SSE streams by visiting `http://localhost:8000/<filename>` and `http://localhost:8000/<filename>/stream`, respectively, in your web browser.

## HTML Template

The `logserver.py` script uses an HTML template file (`log_template.html`) to generate the landing pages for the log files. This template file contains the following placeholders:

- `{filename}`: The name of the log file.
- `{file_contents}`: The contents of the log file.
- `{sse_url}`: The URL for the SSE stream of the log file.

You can modify the HTML template to customize the appearance of the landing pages for the log files.

## Conclusion

The `logserver.py` script provides an easy way to serve log files and their SSE streams via HTTP. By following the steps outlined in this documentation, you can quickly get up and running with this script and customize it to your needs.
