# List

## 1 radio label not rendered in the page
fix the source 

I'm inspired by <1> https://stackoverflow.com/questions/27705968/flask-wtform-radiofield-label-does-not-render
and <2> https://stackoverflow.com/a/31816952/9561380


in flask_bootstrap/templates/bootstrap/wtf.html
```

{% macro form_field(field,
                    form_type="basic",
                    horizontal_columns=('lg', 2, 10),
                    button_map={}) %}

...
{%- elif field.type == 'RadioField' -%}
  {# note: A cleaner solution would be rendering depending on the widget,
     this is just a hack for now, until I can think of something better
     #}
  {{field.label(class="control-label")|safe}}     {# it missed the label render sentence! add this by self #}
  {% call _hz_form_wrap(horizontal_columns, form_type, True, required=required) %}
    {% for item in field -%}
      <div class="radio">
        <label>          
          {{item|safe}} {{item.label.text|safe}} 
        </label>
      </div>
    {% endfor %}
  {% endcall %}
{%- elif field.type == 'SubmitField' -%}
...

```                    

we better render the form mannually instead of use `wtf.quick_form` if we dont do it hackly.


## hack step 

0. connect the docker container, cd `/usr/local/lib/python3.6/site-packages/flask_bootstrap/templates/bootstrap`
1. vim wtf.html
2. find the macro form_field, update the macro body
3. review the page from browser.

> if you didn't install vim in the image or container, use `apt-get update && apt-get install vim`



