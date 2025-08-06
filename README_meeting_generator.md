# Meeting Invitation Generator

A lightweight web application that automates creating personalized Outlook meeting invitations. The app is self-contained, uses only Python's standard library for the backend, and runs in any modern browser without third-party frameworks.

## Features

### User Interface
- **Responsive Design**: Figma-style light-themed form built with vanilla HTML, CSS, and JavaScript
- **Smart Recipients**: Enter multiple recipients as "email, first name" (one per line) with automatic comma insertion
- **Complete Meeting Details**: Subject, start/end date/time picker, location, and organizer email
- **Flexible Body Content**: Four different ways to create meeting content

### Meeting Body Options

1. **Upload Text**: 
   - Supports .txt, .doc, .docx, and .pdf files
   - Live preview for text files
   - Automatic text extraction

2. **Generate Automatically**: 
   - Call any HTTP GET API endpoint
   - Preview generated content before use
   - Error handling for failed requests

3. **Write Your Own**: 
   - Rich textarea with sample template
   - HTML content support with checkbox
   - Personalization with `{{name}}` placeholders

4. **Use Saved Template**: 
   - Dropdown of previously saved templates
   - Preview selected templates
   - Template management system

### Backend Features
- **File Processing**: Extract text from various file formats using only standard library
- **Date Parsing**: Tolerant parsing of various date/time formats
- **Personalization**: Replace `{{name}}` placeholders with recipient names
- **Template System**: Save and load reusable meeting body templates
- **RFC 5545 Compliance**: Generate proper .ics files for Outlook compatibility
- **HTML Support**: Include HTML content with automatic plain text conversion
- **ZIP Download**: Package individual .ics files for easy distribution

## Quick Start

1. **Start the Server**:
   ```bash
   python3 server.py
   ```

2. **Open Your Browser**:
   Navigate to `http://localhost:8000`

3. **Create Meeting Invitations**:
   - Fill in recipients (format: `email@domain.com, First Name`)
   - Add meeting details (subject, date/time, location)
   - Choose body content method
   - Click "Generate Meeting Invitations"
   - Download the ZIP file containing individual .ics files

## File Structure

```
meeting-invitation-generator/
├── server.py              # Python backend server
├── meeting_invites.html   # Main HTML form
├── styles.css             # Figma-style CSS
├── script.js              # Frontend JavaScript
├── templates/             # Saved body templates (auto-created)
├── uploads/               # Temporary file uploads (auto-created)
└── README_meeting_generator.md
```

## Usage Guide

### Adding Recipients
Enter one recipient per line in the format:
```
john.doe@company.com, John
jane.smith@company.com, Jane
```

The system will automatically add commas when you press Enter after typing an email address.

### Meeting Body Content

#### Template Variables
Use `{{name}}` in your content to personalize messages:
```
Dear {{name}},

You are invited to our team meeting...
```

#### HTML Content
Check the "Content is HTML formatted" box when pasting Outlook-style HTML content. The system will:
- Embed HTML in the calendar invite using `X-ALT-DESC` property
- Generate a plain text version by stripping HTML tags
- Ensure compatibility with email clients

#### File Upload Support
- **TXT**: Direct text extraction with encoding detection
- **DOCX**: Extracts text from Word documents using ZIP/XML parsing
- **PDF**: Basic text extraction (limited functionality)

### Template Management
1. **Save Templates**: Enter content, provide a name, click "Save Template"
2. **Load Templates**: Select from dropdown, preview content
3. **Refresh**: Update template list if files change externally

### Generated ICS Files
Each recipient gets a personalized .ics file containing:
- Unique UID for the event
- Proper RFC 5545 formatting
- Personalized content with recipient's name
- ATTENDEE information with RSVP settings
- HTML content support (when applicable)
- Proper line folding for long content

## Technical Details

### Dependencies
- **Backend**: Python 3.6+ (standard library only)
- **Frontend**: Modern web browser with JavaScript enabled

### Supported File Formats
- **Text Files**: .txt (UTF-8, Latin-1, CP1252 encoding support)
- **Word Documents**: .docx (XML parsing from ZIP structure)
- **PDF Files**: Basic text extraction (regex-based, limited)

### Standards Compliance
- **RFC 5545**: iCalendar specification for .ics files
- **HTTP/1.1**: Standard web server implementation
- **HTML5**: Modern form elements and responsive design
- **ES6+**: Modern JavaScript features

### Security Features
- Input validation and sanitization
- Safe filename generation for templates
- HTML escaping for user content
- Limited file size handling

### Browser Compatibility
- Chrome/Chromium 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## API Endpoints

The server provides the following endpoints:

- `GET /` - Serve main application
- `POST /upload_file` - Handle file uploads
- `POST /generate_text` - Call external API for text generation
- `GET /list_templates` - List available templates
- `GET /get_template?name=NAME` - Get template content
- `POST /save_template` - Save new template
- `POST /generate_invitations` - Generate meeting invitations ZIP

## Troubleshooting

### Common Issues

1. **File Upload Fails**:
   - Check file format is supported (.txt, .docx, .pdf)
   - Ensure file is not corrupted
   - Try with a different file

2. **Date/Time Issues**:
   - Use the built-in date/time picker
   - Ensure end time is after start time
   - Check your browser's date/time settings

3. **Template Not Saving**:
   - Ensure template name contains only letters, numbers, spaces, and hyphens
   - Check that content is not empty
   - Verify write permissions in templates directory

4. **ZIP Download Issues**:
   - Check all required fields are filled
   - Verify recipient format is correct
   - Ensure browser allows downloads

### Error Messages
The application provides detailed error messages for:
- Invalid recipient format
- Missing required fields
- File parsing errors
- API call failures
- Template operation issues

## Customization

### Modifying Templates
Edit files in the `templates/` directory or use the web interface.

### Changing Default Content
Modify the default template in `script.js` around line 150.

### Styling Changes
Edit `styles.css` to customize the appearance. The CSS uses CSS custom properties for easy theming.

### Server Configuration
Modify the `PORT` constant in `server.py` to change the default port (8000).

## License

This project uses only Python standard library modules and vanilla web technologies. No external dependencies or licenses required.

## Support

For issues or questions:
1. Check the browser console for JavaScript errors
2. Review server console output for backend errors
3. Verify file permissions for templates and uploads directories
4. Test with different file formats if upload fails

The application is designed to work offline and requires no external services except for the optional API text generation feature.