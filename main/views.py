import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from main.forms import LoginForm, AddSnippetForm
from main.models import Snippet


def get_base_context(request, pagename):
    return {
        'pagename': pagename,
        'loginform': LoginForm(),
        'user': request.user,
    }


def index_page(request):
    context = get_base_context(request, 'PythonBin')
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    anon = "Anonymous User"
    context = get_base_context(request, 'Добавление нового сниппета')
    if request.method == 'POST':
        addform = AddSnippetForm(request.POST)
        if addform.is_valid():
            record = Snippet(
                user=request.user if request.user.is_authenticated else None,
                name=addform.data['name'],
                code=addform.data['code'],
                creation_date=datetime.datetime.now(),
            )
            record.save()
            id = record.id
            messages.add_message(request, messages.SUCCESS, "Сниппет успешно добавлен")
            return redirect('view_snippet', id=id)
        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме")
            return redirect('add_snippet')
    else:
        context['addform'] = AddSnippetForm(
            initial={
                'user': request.user.username if request.user.is_authenticated else "Anonymous User",
            }
        )
    return render(request, 'pages/add_snippet.html', context)


def view_snippet_page(request, id):
    context = get_base_context(request, 'Просмотр сниппета')
    try:
        record = Snippet.objects.get(id=id)
        context['addform'] = AddSnippetForm(
            initial={
                'user': "Anonymous User" if record.user is None else request.user.username,
                'name': record.name,
            }
        )
        context["code"] = highlight(record.code, PythonLexer(), HtmlFormatter())
        context["code_css"] = HtmlFormatter().get_style_defs(".highlight")

    except Snippet.DoesNotExist:
        raise Http404
    return render(request, 'pages/view_snippet.html', context)


def login_page(request):
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.data['username']
            password = loginform.data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, "Авторизация успешна")
            else:
                messages.add_message(request, messages.ERROR, "Неправильный логин или пароль")
        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме авторизации")
    return redirect('index')


def logout_page(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Вы успешно вышли из аккаунта")
    return redirect('index')

@login_required(login_url=login_page)
def my_snippets_page(request):
    context: dict = get_base_context(request=request, pagename="Мои сниппеты")
    context["data"] = Snippet.objects.filter(user=request.user)
    return render(request, "pages/my_snippets.html", context)