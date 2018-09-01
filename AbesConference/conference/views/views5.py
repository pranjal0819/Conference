from django.http import HttpResponse
from django.template.loader import render_to_string


def create(request, slug):
    name = slug
    file_name = name + '.py'
    print(name, file_name)
    message = render_to_string('create_model.html', {
        'app_name': name,
    })
    fo = open(file_name, 'w+')
    fo.write(message)
    fo.close()
    return HttpResponse('Successfully created for ' + slug)
