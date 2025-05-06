from django.core.management.base import BaseCommand
from django.core.management import call_command
import sys
from django.core.management.commands.runserver import Command

class Command(Command):
    help = "Önce testleri çalıştırır, sonra sunucuyu başlatır"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n=== Testler çalıştırılıyor ==="))
        
        try:
            call_command("test", interactive=False)
            self.stdout.write(self.style.SUCCESS("✓ Tüm testler başarılı!"))
            self.stdout.write(self.style.HTTP_SUCCESS("\nSunucu başlatılıyor..."))
            super().handle(*args, **options)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR("✘ Testler başarısız!"))
            sys.exit(1)
                