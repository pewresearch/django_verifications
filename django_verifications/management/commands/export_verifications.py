from django.core.management.base import BaseCommand, CommandError

from tqdm import tqdm


class Command(BaseCommand):

    help = ""

    def add_arguments(self, parser):

        parser.add_argument("model_name", type=str)
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):

        pass
