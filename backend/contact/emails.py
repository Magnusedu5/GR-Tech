import resend
from django.conf import settings


def send_notification(inquiry):
    """Send an email to the GR TECH team when a new inquiry arrives."""
    if not settings.RESEND_API_KEY or not settings.NOTIFICATION_EMAIL:
        return  # Skip silently in dev when keys aren't set

    resend.api_key = settings.RESEND_API_KEY

    resend.Emails.send({
        'from': 'GR TECH Contact <onboarding@resend.dev>',
        'to':   [settings.NOTIFICATION_EMAIL],
        'subject': f'New Inquiry — {inquiry.get_project_type_display()} from {inquiry.name}',
        'html': f"""
        <div style="font-family:sans-serif;max-width:560px;margin:0 auto;">
          <h2 style="color:#BF8C2C;margin-bottom:4px;">New Inquiry</h2>
          <p style="color:#666;font-size:13px;margin-top:0;">{inquiry.created_at:%d %B %Y at %H:%M UTC}</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <table style="width:100%;font-size:14px;border-collapse:collapse;">
            <tr><td style="padding:8px 0;color:#999;width:120px;">Name</td>
                <td style="padding:8px 0;font-weight:500;">{inquiry.name}</td></tr>
            <tr><td style="padding:8px 0;color:#999;">Email</td>
                <td style="padding:8px 0;"><a href="mailto:{inquiry.email}">{inquiry.email}</a></td></tr>
            <tr><td style="padding:8px 0;color:#999;">Project Type</td>
                <td style="padding:8px 0;">{inquiry.get_project_type_display()}</td></tr>
          </table>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <p style="font-size:14px;color:#333;line-height:1.7;white-space:pre-wrap;">{inquiry.message}</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <p style="font-size:12px;color:#999;">
            Reply directly to <a href="mailto:{inquiry.email}">{inquiry.email}</a>
          </p>
        </div>
        """,
        'reply_to': inquiry.email,
    })
