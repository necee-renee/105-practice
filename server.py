#!/usr/bin/env python3
"""
Meeting Invitation Generator Server
A lightweight web application that creates personalized Outlook meeting invitations.
Uses only Python's standard library.
"""

import http.server
import socketserver
import urllib.parse
import json
import os
import re
import zipfile
import io
import tempfile
import shutil
from datetime import datetime
import uuid
import html
import cgi

# Constants
PORT = 8000
TEMPLATES_DIR = "templates"
UPLOADS_DIR = "uploads"

class MeetingInviteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Ensure directories exist
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.path = '/meeting_invites.html'
        elif self.path == '/list_templates':
            self.handle_list_templates()
            return
        elif self.path.startswith('/get_template'):
            self.handle_get_template()
            return
        
        # Serve static files
        super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/upload_file':
            self.handle_file_upload()
        elif self.path == '/generate_text':
            self.handle_text_generation()
        elif self.path == '/save_template':
            self.handle_save_template()
        elif self.path == '/generate_invitations':
            self.handle_generate_invitations()
        else:
            self.send_error(404, "Not Found")

    def handle_file_upload(self):
        """Handle file upload and text extraction"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('content-type')
            if not content_type or not content_type.startswith('multipart/form-data'):
                self.send_json_response({'success': False, 'error': 'Invalid content type'})
                return

            # Parse the form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )

            if 'file' not in form:
                self.send_json_response({'success': False, 'error': 'No file uploaded'})
                return

            file_item = form['file']
            if not file_item.filename:
                self.send_json_response({'success': False, 'error': 'No file selected'})
                return

            # Save uploaded file temporarily
            filename = file_item.filename.lower()
            file_data = file_item.file.read()
            
            # Extract text based on file type
            try:
                if filename.endswith('.txt'):
                    content = self.extract_text_from_txt(file_data)
                elif filename.endswith('.docx'):
                    content = self.extract_text_from_docx(file_data)
                elif filename.endswith('.pdf'):
                    content = self.extract_text_from_pdf(file_data)
                else:
                    raise ValueError("Unsupported file format")

                self.send_json_response({'success': True, 'content': content})

            except Exception as e:
                self.send_json_response({'success': False, 'error': f'Error extracting text: {str(e)}'})

        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error processing upload: {str(e)}'})

    def extract_text_from_txt(self, file_data):
        """Extract text from .txt file"""
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return file_data.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, use error handling
        return file_data.decode('utf-8', errors='replace')

    def extract_text_from_docx(self, file_data):
        """Extract text from .docx file using standard library"""
        import zipfile
        import xml.etree.ElementTree as ET
        
        try:
            # DOCX is a ZIP file containing XML
            with zipfile.ZipFile(io.BytesIO(file_data)) as docx_zip:
                # Read the main document
                document_xml = docx_zip.read('word/document.xml')
                
                # Parse XML and extract text
                root = ET.fromstring(document_xml)
                
                # Find all text elements (w:t tags)
                text_elements = []
                for elem in root.iter():
                    if elem.tag.endswith('}t'):  # w:t tag
                        if elem.text:
                            text_elements.append(elem.text)
                
                return '\n'.join(text_elements)
        
        except Exception as e:
            raise ValueError(f"Could not parse DOCX file: {str(e)}")

    def extract_text_from_pdf(self, file_data):
        """Basic PDF text extraction using standard library (limited functionality)"""
        try:
            # This is a very basic PDF text extractor
            # It looks for text between 'BT' and 'ET' operators
            content = file_data.decode('latin-1', errors='ignore')
            
            # Find text content between BT (Begin Text) and ET (End Text)
            import re
            text_pattern = r'BT\s*(.*?)\s*ET'
            text_blocks = re.findall(text_pattern, content, re.DOTALL)
            
            extracted_text = []
            for block in text_blocks:
                # Look for text in parentheses or brackets
                text_matches = re.findall(r'[\(\[]([^\)\]]+)[\)\]]', block)
                for match in text_matches:
                    # Clean up the text
                    clean_text = re.sub(r'\\[rn]', '\n', match)
                    clean_text = re.sub(r'\\(.)', r'\1', clean_text)
                    if len(clean_text.strip()) > 2:  # Ignore very short strings
                        extracted_text.append(clean_text.strip())
            
            result = '\n'.join(extracted_text)
            
            if not result.strip():
                return "PDF text extraction is limited. Please use a plain text file for better results."
            
            return result
            
        except Exception as e:
            raise ValueError(f"Could not parse PDF file: {str(e)}")

    def handle_text_generation(self):
        """Handle API text generation"""
        try:
            content_length = int(self.headers['content-length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            endpoint = data.get('endpoint')
            if not endpoint:
                self.send_json_response({'success': False, 'error': 'No endpoint provided'})
                return

            # Make HTTP GET request to the API endpoint
            import urllib.request
            
            try:
                with urllib.request.urlopen(endpoint, timeout=30) as response:
                    content = response.read().decode('utf-8')
                    self.send_json_response({'success': True, 'content': content})
            
            except urllib.error.URLError as e:
                self.send_json_response({'success': False, 'error': f'API request failed: {str(e)}'})
            except Exception as e:
                self.send_json_response({'success': False, 'error': f'Error calling API: {str(e)}'})

        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error processing request: {str(e)}'})

    def handle_list_templates(self):
        """List available templates"""
        try:
            templates = []
            if os.path.exists(TEMPLATES_DIR):
                for filename in os.listdir(TEMPLATES_DIR):
                    if filename.endswith('.txt'):
                        templates.append(filename[:-4])  # Remove .txt extension
            
            self.send_json_response({'success': True, 'templates': templates})
        
        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error listing templates: {str(e)}'})

    def handle_get_template(self):
        """Get template content"""
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            template_name = params.get('name', [None])[0]
            if not template_name:
                self.send_json_response({'success': False, 'error': 'No template name provided'})
                return

            template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.txt")
            
            if not os.path.exists(template_path):
                self.send_json_response({'success': False, 'error': 'Template not found'})
                return

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_json_response({'success': True, 'content': content})
        
        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error loading template: {str(e)}'})

    def handle_save_template(self):
        """Save template"""
        try:
            content_length = int(self.headers['content-length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            name = data.get('name', '').strip()
            content = data.get('content', '')
            
            if not name:
                self.send_json_response({'success': False, 'error': 'Template name is required'})
                return
            
            if not content.strip():
                self.send_json_response({'success': False, 'error': 'Template content is required'})
                return

            # Sanitize filename
            safe_name = re.sub(r'[^\w\s-]', '', name).strip()
            if not safe_name:
                self.send_json_response({'success': False, 'error': 'Invalid template name'})
                return

            template_path = os.path.join(TEMPLATES_DIR, f"{safe_name}.txt")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.send_json_response({'success': True, 'message': 'Template saved successfully'})
        
        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error saving template: {str(e)}'})

    def handle_generate_invitations(self):
        """Generate meeting invitations and return ZIP file"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('content-type')
            if not content_type or not content_type.startswith('multipart/form-data'):
                self.send_json_response({'success': False, 'error': 'Invalid content type'})
                return

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )

            # Extract form data
            data = {}
            for key in form.keys():
                data[key] = form[key].value

            # Validate required fields
            required_fields = ['recipients', 'subject', 'startDateTime', 'endDateTime', 'bodyContent']
            for field in required_fields:
                if field not in data or not data[field].strip():
                    self.send_json_response({'success': False, 'error': f'Missing required field: {field}'})
                    return

            # Parse recipients
            recipients = self.parse_recipients(data['recipients'])
            if not recipients:
                self.send_json_response({'success': False, 'error': 'No valid recipients found'})
                return

            # Parse dates
            try:
                start_dt = self.parse_datetime(data['startDateTime'])
                end_dt = self.parse_datetime(data['endDateTime'])
            except ValueError as e:
                self.send_json_response({'success': False, 'error': f'Invalid date format: {str(e)}'})
                return

            # Generate ICS files
            ics_files = []
            for email, name in recipients:
                ics_content = self.generate_ics_file(
                    recipient_email=email,
                    recipient_name=name,
                    subject=data['subject'],
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    location=data.get('location', ''),
                    organizer=data.get('organizer', ''),
                    body_content=data['bodyContent'],
                    is_html=data.get('isHtml', 'false').lower() == 'true'
                )
                
                filename = f"{name.replace(' ', '_')}_{email.split('@')[0]}_meeting.ics"
                ics_files.append((filename, ics_content))

            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, content in ics_files:
                    zip_file.writestr(filename, content)
            
            zip_data = zip_buffer.getvalue()

            # Send ZIP file
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', 'attachment; filename="meeting_invitations.zip"')
            self.send_header('Content-Length', str(len(zip_data)))
            self.end_headers()
            self.wfile.write(zip_data)

        except Exception as e:
            self.send_json_response({'success': False, 'error': f'Error generating invitations: {str(e)}'})

    def parse_recipients(self, recipients_text):
        """Parse recipients from text"""
        recipients = []
        lines = recipients_text.strip().split('\n')
        
        email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parts = [part.strip() for part in line.split(',')]
            if len(parts) == 2:
                email, name = parts
                if email_regex.match(email) and name:
                    recipients.append((email, name))
        
        return recipients

    def parse_datetime(self, datetime_str):
        """Parse datetime string with tolerance for various formats"""
        # Handle ISO format from HTML datetime-local input
        if 'T' in datetime_str:
            try:
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Try other common formats
        formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse datetime: {datetime_str}")

    def generate_ics_file(self, recipient_email, recipient_name, subject, start_datetime, 
                         end_datetime, location, organizer, body_content, is_html=False):
        """Generate RFC 5545 compliant ICS file"""
        
        # Generate unique UID
        uid = f"{uuid.uuid4()}@meeting-generator"
        
        # Format datetimes in UTC (basic implementation)
        start_utc = start_datetime.strftime('%Y%m%dT%H%M%S')
        end_utc = end_datetime.strftime('%Y%m%dT%H%M%S')
        created = datetime.now().strftime('%Y%m%dT%H%M%SZ')
        
        # Personalize body content
        personalized_body = body_content.replace('{{name}}', recipient_name)
        
        # Create plain text version if HTML
        if is_html:
            # Simple HTML to text conversion
            import re
            plain_text = re.sub(r'<[^>]+>', '', personalized_body)
            plain_text = html.unescape(plain_text)
            plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        else:
            plain_text = personalized_body
        
        # Build ICS content
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Meeting Generator//Meeting Generator 1.0//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:REQUEST',
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTAMP:{created}',
            f'DTSTART:{start_utc}',
            f'DTEND:{end_utc}',
            f'SUMMARY:{self.fold_line(subject)}',
        ]
        
        if location:
            lines.append(f'LOCATION:{self.fold_line(location)}')
        
        if organizer:
            lines.append(f'ORGANIZER:mailto:{organizer}')
        
        # Add attendee
        lines.append(f'ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={recipient_name}:mailto:{recipient_email}')
        
        # Add description
        escaped_description = self.escape_ics_text(plain_text)
        lines.append(f'DESCRIPTION:{self.fold_line(escaped_description)}')
        
        # Add HTML description if applicable
        if is_html:
            escaped_html = self.escape_ics_text(personalized_body)
            lines.append(f'X-ALT-DESC;FMTTYPE=text/html:{self.fold_line(escaped_html)}')
        
        lines.extend([
            'STATUS:CONFIRMED',
            'TRANSP:OPAQUE',
            'END:VEVENT',
            'END:VCALENDAR'
        ])
        
        return '\r\n'.join(lines) + '\r\n'

    def escape_ics_text(self, text):
        """Escape text for ICS format"""
        # Escape special characters according to RFC 5545
        text = text.replace('\\', '\\\\')
        text = text.replace(';', '\\;')
        text = text.replace(',', '\\,')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '')
        return text

    def fold_line(self, line, max_length=75):
        """Fold long lines according to RFC 5545"""
        if len(line) <= max_length:
            return line
        
        folded = []
        while len(line) > max_length:
            folded.append(line[:max_length])
            line = ' ' + line[max_length:]  # Continuation line starts with space
        
        if line.strip():  # Add remaining part if not empty
            folded.append(line)
        
        return '\r\n'.join(folded)

    def send_json_response(self, data):
        """Send JSON response"""
        response_data = json.dumps(data).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)

    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """Start the server"""
    print(f"Starting Meeting Invitation Generator Server on port {PORT}")
    print(f"Open your browser to: http://localhost:{PORT}")
    print(f"Templates directory: {os.path.abspath(TEMPLATES_DIR)}")
    print(f"Uploads directory: {os.path.abspath(UPLOADS_DIR)}")
    
    try:
        with socketserver.TCPServer(("", PORT), MeetingInviteHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()