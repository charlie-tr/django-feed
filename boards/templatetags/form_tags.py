from django import template

register = template.Library()

@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__

@register.filter
def input_class(bound_field):
    css_class = ''
    if bound_field.form.is_bound: #bound tức là đang cần có đủ thông tin
        if bound_field.errors: #again, work hidden
            css_class = 'is-invalid'
        elif field_type(bound_field) != 'PasswordInput': #only consider non-password fields, hơi buồn cười
            css_class = 'is-valid'
    return 'form-control {}'.format(css_class)