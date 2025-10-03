from flask import Flask, render_template, send_file, request, url_for, jsonify
from datetime import datetime, timedelta, timezone
from dateutil import tz
import io, qrcode

app = Flask(__name__)

EVENT = {
    "celebrant_name": "Anna",
    "degree": "Laurea in CTF",
    "host_name": "Nicola",
    "title": "Festa di Laurea – Rose & Halloween",
    "subtitle": "Tra rose dorate e un tocco di Halloween ✨🎃",
    "date_iso": "2025-10-31T20:30:00+01:00",
    "venue": "Jammo addò Sandrissimo",
    "address": "Piazza Umberto I, 8, 83042 Atripalda AV",
    "gmaps_url": "https://www.google.com/maps?q=Jammo%20add%C3%B2%20Sandrissimo%2C%20Piazza%20Umberto%20I%2C%208%2C%2083042%20Atripalda%20AV",
    "rsvp_whatsapp": "https://wa.me/39XXXXXXXXXX?text=Ciao%20Nicola%2C%20confermo%20la%20mia%20presenza%20alla%20festa%20di%20laurea!",
    "entry_password": "rosagold",
    "theme": {"gold":"#b08900"}
}
ROME = tz.gettz("Europe/Rome")

def parse_event_start():
    dt = datetime.fromisoformat(EVENT["date_iso"])
    if dt.tzinfo is None: dt = dt.replace(tzinfo=ROME)
    return dt

def dt_utc_string(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

@app.route("/")
def home():
    guest = request.args.get("guest") or ""
    start = parse_event_start()
    end = start + timedelta(hours=2)
    wa_text = (f"Sei invitato alla festa di laurea di {EVENT['celebrant_name']}!\n\n"
               f"{EVENT['title']}\n"
               f"{start.astimezone(ROME).strftime('%A %d %B %Y, %H:%M')}\n"
               f"{EVENT['venue']} – {EVENT['address']}\n"
               "Dress code: un tocco di rosa e oro (Halloween-friendly!).\n"
               "Apri l'invito qui: {URL}\n"
               "RSVP entro il 27/10. Ti aspettiamo!")
    formatted_time = start.astimezone(ROME).strftime('%A %d %B %Y, %H:%M')
    return render_template("invite.html", event=EVENT, start=start, end=end, wa_text=wa_text, guest=guest, formatted_time=formatted_time)

@app.route("/download.ics")
def download_ics():
    start = parse_event_start()
    end = start + timedelta(hours=2)
    ics = "\n".join(["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Nicola//Invito Laurea//IT","BEGIN:VEVENT",        f"UID:invito-{start.timestamp()}@invito.local",f"DTSTAMP:{dt_utc_string(datetime.now(timezone.utc))}",        f"DTSTART:{dt_utc_string(start)}",f"DTEND:{dt_utc_string(end)}",        f"SUMMARY:{EVENT['title']}",f"LOCATION:{EVENT['venue']} — {EVENT['address']}",        f"DESCRIPTION:{EVENT['celebrant_name']} si laurea in CTF! Dress code: rosa & dettagli dorati, con un tocco Halloween.",        "END:VEVENT","END:VCALENDAR"]) 
    return send_file(io.BytesIO(ics.encode("utf-8")), mimetype="text/calendar", as_attachment=True, download_name="invito-laurea.ics")

@app.route("/qr.png")
def qr():
    base_url = request.url_root.rstrip("/")
    guest = request.args.get("guest")
    url = f"{base_url}/" + (f"?guest={guest}" if guest else "")
    buf = io.BytesIO(); qrcode.make(url).save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/health")
def health():
    return jsonify({"status":"ok"})
    
if __name__ == "__main__": app.run(debug=True)
