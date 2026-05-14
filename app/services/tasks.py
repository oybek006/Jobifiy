import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.services.celery_app import celery_app
from app.core.config import settings


def send_email_sync(to_email: str, subject: str, html_body: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.MAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email yuborishda xato: {e}")
        return False


@celery_app.task(name="send_welcome_email", bind=True, max_retries=3)
def send_welcome_email(self, to_email: str, full_name: str):
    """Ro'yxatdan o'tgandan keyin xush kelibsiz emaili."""
    html = f"""
    <html><body>
    <h2>Assalomu alaykum, {full_name}!</h2>
    <p>Jobify platformasiga xush kelibsiz!</p>
    <p>Endi siz:</p>
    <ul>
        <li>O'z profilingizni to'ldiring</li>
        <li>Resume yuklang</li>
        <li>Vakansiyalarni ko'ring va ariza topshiring</li>
    </ul>
    <p>Muvaffaqiyatlar!</p>
    <p><b>Jobify jamoasi</b></p>
    </body></html>
    """
    try:
        send_email_sync(to_email, "Jobify — Xush kelibsiz!", html)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_application_received_email", bind=True, max_retries=3)
def send_application_received_email(
    self, hr_email: str, candidate_name: str, vacancy_title: str
):
    """HR ga yangi ariza haqida email."""
    html = f"""
    <html><body>
    <h2>Yangi ariza keldi!</h2>
    <p><b>{candidate_name}</b> sizning <b>"{vacancy_title}"</b> vakansiyangizga ariza topshirdi.</p>
    <p>Admin panelingizga kiring va arizani ko'rib chiqing.</p>
    <p><b>Jobify jamoasi</b></p>
    </body></html>
    """
    try:
        send_email_sync(hr_email, f"Yangi ariza: {vacancy_title}", html)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_status_update_email", bind=True, max_retries=3)
def send_status_update_email(
    self, candidate_email: str, candidate_name: str,
    vacancy_title: str, new_status: str
):
    """Kandidatga ariza holati o'zgarganda email."""
    status_messages = {
        "reviewing": "Ko'rib chiqilmoqda",
        "interview": "Suhbatga taklif etildingiz! 🎉",
        "accepted": "Tabriklaymiz! Arizangiz qabul qilindi 🎊",
        "rejected": "Afsuski, bu safar qabul qilinmadi",
        "withdrawn": "Ariza qaytarib olindi",
    }
    status_text = status_messages.get(new_status, new_status)

    html = f"""
    <html><body>
    <h2>Ariza holati yangilandi</h2>
    <p>Assalomu alaykum, <b>{candidate_name}</b>!</p>
    <p><b>"{vacancy_title}"</b> vakansiyasiga arizangiz holati:</p>
    <h3 style="color: #2563eb;">{status_text}</h3>
    <p>Batafsil ma'lumot uchun Jobify saytiga kiring.</p>
    <p><b>Jobify jamoasi</b></p>
    </body></html>
    """
    try:
        send_email_sync(candidate_email, f"Ariza holati: {vacancy_title}", html)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
