import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

MODELS_CODE = '''class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        return "Question: " + self.content

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)'''

ADMIN_CODE = '''from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


# <HINT> Register Question and Choice models here

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)'''

VIEWS_CODE = '''# <HINT> Create a submit view to create an exam submission record for a course enrollment,
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,)))


# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()  # Assuming course has related questions

    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)  # Get all correct choices for the question
        selected_choices = choices.filter(question=question)  # Get the user's selected choices for the question

        # Check if the selected choices are the same as the correct choices
        if set(correct_choices) == set(selected_choices):
            total_score += question.grade  # Add the question's grade only if all correct answers are selected

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)'''

URLS_CODE = '''from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    # ex: /onlinecourse/5/
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    # ex: /enroll/5/
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # <HINT> Create a route for submit view
    path('<int:course_id>/submit/', views.submit, name="submit"),
    # <HINT> Create a route for show_exam_result view
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name="exam_result"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)'''

def render_code_to_html(code, title, filename_html, with_line_numbers=False):
    formatter = HtmlFormatter(style='default', linenos='table' if with_line_numbers else False, cssclass='highlight')
    highlighted = highlight(code, PythonLexer(), formatter)
    css = formatter.get_style_defs('.highlight')

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        {css}
        body {{
            background: #ffffff;
            font-family: Consolas, "Courier New", monospace;
            padding: 30px;
            margin: 0;
        }}
        .header {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            color: #666;
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 1px solid #eee;
        }}
        .highlight {{
            background: #ffffff;
            font-size: 15px;
            line-height: 1.5;
        }}
        pre {{
            margin: 0;
            font-family: Consolas, "Courier New", monospace;
        }}
        .linenodiv pre {{
            color: #999;
            padding-right: 15px;
            border-right: 1px solid #ddd;
            user-select: none;
        }}
        td.code {{
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">{title}</div>
    {highlighted}
</body>
</html>'''
    with open(filename_html, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    os.makedirs('ss', exist_ok=True)
    temp_files = [
        ('models.html', MODELS_CODE, 'onlinecourse/models.py', 'ss/01-models.png', False),
        ('admin.html', ADMIN_CODE, 'onlinecourse/admin.py', 'ss/02-admin-file.png', False),
        ('views.html', VIEWS_CODE, 'onlinecourse/views.py', 'ss/05-views.png', False),
        ('urls.html', URLS_CODE, 'onlinecourse/urls.py', 'ss/06-urls.png', True),
    ]

    for html_file, code, title, out_png, line_nums in temp_files:
        render_code_to_html(code, title, html_file, line_nums)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1000, "height": 800})

        for html_file, _, _, out_png, _ in temp_files:
            abs_path = os.path.abspath(html_file).replace('\\\\', '/')
            page.goto(f'file:///{abs_path}')
            page.wait_for_load_state('networkidle')
            # Clip or fullpage
            page.screenshot(path=out_png, full_page=True)
            print(f"Generated {out_png}")
            if os.path.exists(html_file):
                os.remove(html_file)

        browser.close()

if __name__ == '__main__':
    main()
