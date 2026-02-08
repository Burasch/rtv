class LogoModule:
    @staticmethod
    def get_logo_url(channel_data):
        # Holt die ID aus der JSON (z.B. "rossiya-24")
        channel_id = channel_data.get('id', 'tv')
        # Gibt den externen Link zurück
        return f"https://toplogos.ru/images/thumbs/preview-logo-{channel_id}.png"
