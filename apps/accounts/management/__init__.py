from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Skill, Language, GigCategory
from apps.gigs.models import GigCategory

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate initial data for the application'

    def handle(self, *args, **options):
        # Create skills
        skills_data = [
            {'name': 'Python', 'category': 'Programming'},
            {'name': 'JavaScript', 'category': 'Programming'},
            {'name': 'React', 'category': 'Programming'},
            {'name': 'Django', 'category': 'Programming'},
            {'name': 'PHP', 'category': 'Programming'},
            {'name': 'WordPress', 'category': 'Programming'},
            {'name': 'Graphic Design', 'category': 'Design'},
            {'name': 'UI/UX Design', 'category': 'Design'},
            {'name': 'Logo Design', 'category': 'Design'},
            {'name': 'Digital Marketing', 'category': 'Marketing'},
            {'name': 'SEO', 'category': 'Marketing'},
            {'name': 'Content Writing', 'category': 'Writing'},
            {'name': 'Copywriting', 'category': 'Writing'},
            {'name': 'Translation', 'category': 'Writing'},
            {'name': 'Video Editing', 'category': 'Video'},
            {'name': 'Animation', 'category': 'Video'},
        ]

        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={'category': skill_data['category']}
            )
            if created:
                self.stdout.write(f'Created skill: {skill.name}')

        # Create languages
        languages_data = [
            {'name': 'English', 'code': 'en'},
            {'name': 'French', 'code': 'fr'},
            {'name': 'Arabic', 'code': 'ar'},
            {'name': 'Swahili', 'code': 'sw'},
            {'name': 'Hausa', 'code': 'ha'},
            {'name': 'Yoruba', 'code': 'yo'},
            {'name': 'Igbo', 'code': 'ig'},
            {'name': 'Amharic', 'code': 'am'},
        ]

        for lang_data in languages_data:
            language, created = Language.objects.get_or_create(
                name=lang_data['name'],
                defaults={'code': lang_data['code']}
            )
            if created:
                self.stdout.write(f'Created language: {language.name}')

        # Create gig categories
        categories_data = [
            {'name': 'Programming & Tech', 'description': 'Web development, mobile apps, and software development'},
            {'name': 'Design & Creative', 'description': 'Graphic design, UI/UX, and creative services'},
            {'name': 'Digital Marketing', 'description': 'SEO, social media, and online marketing'},
            {'name': 'Writing & Translation', 'description': 'Content writing, copywriting, and translation services'},
            {'name': 'Video & Animation', 'description': 'Video editing, animation, and motion graphics'},
            {'name': 'Music & Audio', 'description': 'Audio editing, voice-over, and music production'},
            {'name': 'Business', 'description': 'Business consulting, data entry, and virtual assistance'},
            {'name': 'Lifestyle', 'description': 'Health, fitness, and lifestyle coaching'},
        ]

        for cat_data in categories_data:
            category, created = GigCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated initial data!')
        )