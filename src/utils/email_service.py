import smtplib
import ssl
from email.message import EmailMessage
import os
from typing import Optional

class EmailService:
    def __init__(self, sender_email: str = "", sender_password: str = ""):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.port = 465  # For SSL
        self.simulated = not (sender_email and sender_password)
        if self.simulated:
            print("[INFO] EmailService running in SIMULATION MODE (No credentials provided).")
            print("[INFO] Alerts will be logged to 'captures/email_log.txt'.")

    def send_alert(self, to_email: str, subject: str, body: str, image_path: Optional[str] = None, alert_details: Optional[dict] = None):
        """
        Send professional HTML email alert with organized cheating details.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body (fallback)
            image_path: Path to screenshot
            alert_details: Dict with keys: student_name, student_id, violation_type, timestamp, severity
        """
        if self.simulated:
            self._log_simulated_email(to_email, subject, body, image_path, alert_details)
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = to_email
        
        # Create HTML email with professional template
        if alert_details:
            html_body = self._create_html_email(alert_details, image_path)
            msg.set_content(body)  # Plain text fallback
            msg.add_alternative(html_body, subtype='html')
        else:
            msg.set_content(body)

        # Attach image
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img_data = f.read()
                img_name = os.path.basename(image_path)
                msg.add_attachment(img_data, maintype="image", subtype="jpeg", filename=img_name)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"[INFO] Alert email sent to {to_email}")
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
    
    def _create_html_email(self, details: dict, image_path: Optional[str] = None) -> str:
        """Create professional HTML email template"""
        student_name = details.get('student_name', 'Unknown Student')
        student_id = details.get('student_id', 'N/A')
        violation_type = details.get('violation_type', 'Unknown Violation')
        timestamp = details.get('timestamp', 'N/A')
        severity = details.get('severity', 'medium')
        
        severity_color = "#dc2626" if severity == "high" else "#f59e0b"
        severity_text = "HIGH PRIORITY" if severity == "high" else "MEDIUM PRIORITY"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f6f9;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .severity-badge {{
                    display: inline-block;
                    background-color: {severity_color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 10px;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-box {{
                    background-color: #fef2f2;
                    border-left: 4px solid {severity_color};
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                .details-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .details-table td {{
                    padding: 12px;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .details-table td:first-child {{
                    font-weight: 600;
                    color: #374151;
                    width: 40%;
                }}
                .screenshot {{
                    width: 100%;
                    border-radius: 8px;
                    margin: 20px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .footer {{
                    background-color: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                }}
                .warning {{
                    color: {severity_color};
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ AI Cheat Detector Alert</h1>
                    <div class="severity-badge">{severity_text}</div>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <p style="margin: 0; font-size: 16px;">
                            <strong>Attention {student_name},</strong><br>
                            A potential academic integrity violation has been detected during your examination.
                        </p>
                    </div>
                    
                    <h2 style="color: #1e293b; margin-top: 30px;">Violation Details</h2>
                    <table class="details-table">
                        <tr>
                            <td>Student Name</td>
                            <td><strong>{student_name}</strong></td>
                        </tr>
                        <tr>
                            <td>Student ID</td>
                            <td>{student_id}</td>
                        </tr>
                        <tr>
                            <td>Violation Type</td>
                            <td class="warning">{violation_type}</td>
                        </tr>
                        <tr>
                            <td>Date & Time</td>
                            <td>{timestamp}</td>
                        </tr>
                        <tr>
                            <td>Severity Level</td>
                            <td class="warning">{severity_text}</td>
                        </tr>
                    </table>
                    
                    <h2 style="color: #1e293b;">Evidence</h2>
                    <p style="color: #6b7280;">The following screenshot was captured at the time of detection:</p>
                    
                    {f'<img src="cid:evidence_image" class="screenshot" alt="Evidence Screenshot">' if image_path else '<p style="color: #9ca3af;">No screenshot available</p>'}
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin-top: 20px; border-radius: 4px;">
                        <p style="margin: 0; color: #92400e;">
                            <strong>⚠️ Important:</strong> This is an automated alert. If you believe this is an error, please contact your exam proctor or administrator immediately.
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from the AI Cheat Detector System.</p>
                    <p>© 2025 AI Cheat Detector | Academic Integrity Monitoring</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _log_simulated_email(self, to_email, subject, body, image_path, alert_details=None):
        log_entry = (
            f"--- SIMULATED EMAIL ---\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Time: {os.path.basename(image_path).split('_')[-1].replace('.jpg', '') if image_path else 'N/A'}\n"
            f"Body: {body}\n"
            f"Attachment: {image_path}\n"
        )
        if alert_details:
            log_entry += f"Details: {alert_details}\n"
        log_entry += f"-----------------------\n"
        
        print(log_entry)
        
        # Save to a log file in the captures directory (assuming image_path is in captures)
        if image_path:
            log_dir = os.path.dirname(image_path)
            log_file = os.path.join(log_dir, "email_log.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

